import requests
from threading import Lock

import source.creds as creds
import source.utils.Utils as Utils

from source.BitrixFieldsAliases import *
from source.BitrixFieldMappings import *
from source.config import *

from source.DealData import DealData

logger = logging.getLogger(__name__)

SESSION = requests.session()
REQUESTS_TIMEOUT = 10
REQUESTS_MAX_ATTEMPTS = 3

# global bitrix worker error code
BW_OK = 0
BW_NO_SUCH_DEAL = 1
BW_WRONG_STAGE = 2
BW_INTERNAL_ERROR = 3

# bitrix dicts
PAYMENT_TYPES = {}
PAYMENT_TYPES_LOCK = Lock()
PAYMENT_METHODS = {}
PAYMENT_METHODS_LOCK = Lock()
FLORISTS = {}
FLORISTS_LOCK = Lock()
COURIERS = {}
COURIERS_LOCK = Lock()
ORDERS_TYPES = {}
ORDERS_TYPES_LOCK = Lock()
DEAL_TIMES = {}
DEAL_TIMES_LOCK = Lock()

# Bitrix OAuth keys
# store in Telegram bot persistence to serialize automatically
OAUTH_LOCK = Lock()


def send_request(method, params=None, handle_next=False):
    if params is None:
        params = {}

    for a in range(REQUESTS_MAX_ATTEMPTS):
        try:
            response = SESSION.post(url=creds.BITRIX_API_URL + method,
                                    json=params, timeout=REQUESTS_TIMEOUT)

            if response and response.ok:
                json = response.json()
                next_counter = json.get('next')
                result = json.get('result')

                # handling List[]
                if result is not None and handle_next and next_counter:
                    params['start'] = next_counter
                    result.extend(send_request(method, params, True))
                    return result

                if result is not None:
                    return result
                else:
                    error = 'Bitrix bad response: %s\n Attempt: %s\n Request params: %s\n Error:%s' \
                            % (json, a, params, json.get('error_description'))
                    logger.error(error)
            else:
                error = 'Bitrix request failed - %s : Attempt: %s : Request params: %s' \
                        % (response.text, a, params)
                logger.error(error)

        except Exception as e:
            error = 'Sending Bitrix api request error %s' % e
            logger.error(error)

    return None


def get_deal(deal_id):
    result = send_request('crm.deal.get', {'id': deal_id})
    return result


def update_deal(deal_id, fields):
    result = send_request('crm.deal.update', {'id': deal_id,
                                              'fields': fields})
    return result


# TODO: batch load if 'next' in result
def _load_userfield_dict(field_id):
    result = {}

    try:
        userfield = send_request('crm.deal.userfield.get', {'id': field_id})
        userfield_list = userfield['LIST']
        result = {el['ID']: el['VALUE'] for el in userfield_list}
    except Exception as e:
        logger.error("Exception getting userfield dict: %s", e)

    return result


def _load_payment_types():
    global PAYMENT_TYPES
    result = _load_userfield_dict(PAYMENT_TYPE_FIELD_ID)

    if result:
        with PAYMENT_TYPES_LOCK:
            PAYMENT_TYPES = result


def _load_payment_methods():
    global PAYMENT_METHODS
    result = _load_userfield_dict(PAYMENT_METHOD_FIELD_ID)

    if result:
        with PAYMENT_METHODS_LOCK:
            PAYMENT_METHODS = result


def _load_couriers():
    global COURIERS
    result = _load_userfield_dict(COURIER_FIELD_ID)

    if result:
        with COURIERS_LOCK:
            COURIERS = result


def _load_orders_types():
    global ORDERS_TYPES
    result = _load_userfield_dict(ORDER_TYPE_FIELD_ID)

    if result:
        with ORDERS_TYPES_LOCK:
            ORDERS_TYPES = result


def _load_deal_times():
    global DEAL_TIMES
    result = _load_userfield_dict(DEAL_TIME_FIELD_ID)

    if result:
        with DEAL_TIMES_LOCK:
            DEAL_TIMES = result


def _load_florists():
    result = {}
    params = {USER_POSITION_ALIAS: FLORIST_POSITION_ID}

    try:
        florists = send_request('user.get', params, handle_next=True)

        result = {f['ID']: Utils.prepare_external_field(f, 'NAME') + ' ' + Utils.prepare_external_field(f, 'LAST_NAME')
                  for f in florists if f['ACTIVE']}  # self-filtering active users - due to bug in Bitrix24 API

    except Exception as e:
        logging.error("Exception getting florists, %s", e)

    global FLORISTS
    if result:
        with FLORISTS_LOCK:
            FLORISTS = result


def load_dicts():
    _load_couriers()
    _load_florists()
    _load_payment_methods()
    _load_payment_types()
    _load_orders_types()
    _load_deal_times()


def process_deal_info(deal_id, check_approved=True):
    deal = get_deal(deal_id)

    deal_data = DealData()
    deal_data.deal_id = deal_id

    if not deal:
        return BW_NO_SUCH_DEAL, deal_data

    if check_approved and deal[DEAL_STAGE_ALIAS] != DEAL_IS_IN_APPROVED_STAGE:
        return BW_WRONG_STAGE, deal_data

    deal_data.order = Utils.prepare_external_field(deal, DEAL_ORDER_ALIAS)

    contact_id = deal.get(DEAL_CONTACT_ALIAS)
    contact_data = send_request('crm.contact.get',
                                {'id': contact_id})

    contact_name = Utils.prepare_external_field(contact_data, CONTACT_USER_NAME_ALIAS)
    contact_phone = ''

    if contact_data and contact_data.get(CONTACT_HAS_PHONE_ALIAS) == CONTACT_HAS_PHONE:
        contact_phone = Utils.prepare_external_field(contact_data[CONTACT_PHONE_ALIAS][0], 'VALUE')

    deal_data.contact = contact_name + ' ' + contact_phone
    deal_data.order_received_by = Utils.prepare_external_field(deal, DEAL_ORDER_RECEIVED_BY_ALIAS)
    deal_data.total_sum = Utils.prepare_external_field(deal, DEAL_TOTAL_SUM_ALIAS)

    payment_type_id = Utils.prepare_external_field(deal, DEAL_PAYMENT_TYPE_ALIAS)
    deal_data.payment_type = Utils.prepare_external_field(PAYMENT_TYPES, payment_type_id, PAYMENT_TYPES_LOCK)

    payment_method_id = Utils.prepare_external_field(deal, DEAL_PAYMENT_METHOD_ALIAS)

    deal_data.payment_method = Utils.prepare_external_field(PAYMENT_METHODS, payment_method_id, PAYMENT_METHODS_LOCK)

    deal_data.payment_status = Utils.prepare_external_field(deal, DEAL_PAYMENT_STATUS_ALIAS)
    deal_data.prepaid = Utils.prepare_external_field(deal, DEAL_PREPAID_ALIAS)
    deal_data.to_pay = Utils.prepare_external_field(deal, DEAL_TO_PAY_ALIAS)
    deal_data.incognito = Utils.prepare_deal_incognito_operator(deal, DEAL_INCOGNITO_ALIAS)
    deal_data.order_comment = Utils.prepare_external_field(deal, DEAL_ORDER_COMMENT_ALIAS)
    deal_data.delivery_comment = Utils.prepare_external_field(deal, DEAL_DELIVERY_COMMENT_ALIAS)
    deal_data.courier_id = Utils.prepare_external_field(deal, DEAL_COURIER_ALIAS)
    deal_data.florist_id = Utils.prepare_external_field(deal, DEAL_FLORIST_NEW_ALIAS)
    deal_data.order_type_id = Utils.prepare_external_field(deal, DEAL_ORDER_TYPE_ALIAS)

    return BW_OK, deal_data


def get_file_dl_url(bitrix_file_id):
    file = send_request('disk.file.get',
                        {'id': bitrix_file_id})

    dl_url = file.get(DISK_FILE_DL_URL_ALIAS)

    if not dl_url:
        logger.error('Error loading Bitrix file metadata: no URL provided')
        return None

    return dl_url


def refresh_oauth(refresh_token):
    for a in range(REQUESTS_MAX_ATTEMPTS):
        try:
            response = SESSION.get(
                url=creds.BITRIX_OAUTH_REFRESH_URL.format(refresh_token),
                timeout=REQUESTS_TIMEOUT)

            if response and response.ok:
                json = response.json()

                access_token = json.get('access_token')
                refresh_token = json.get('refresh_token')

                logger.info('OAuth refreshed')
                return access_token, refresh_token
            else:
                logger.error("Error OAuth refreshing: %s", response)

        except Exception as e:
            error = 'Bitrix OAuth refresh exception %s' % e
            logger.error(error)

    return None, None
