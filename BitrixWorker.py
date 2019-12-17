import requests
import creds
import logging
import TextSnippets


class BitrixWorker:
    SESSION = requests.session()
    REQUESTS_TIMEOUT = 10
    REQUESTS_MAX_ATTEMPTS = 3

    COURIER_FIELD_ID = '1009'  # hardcoded for now
    TITLE_ALIAS = 'TITLE'
    DEAL_ID_ALIAS = 'ID'
    COURIER_FIELD_ALIAS = 'UF_CRM_1577117931'
    ADDRESS_ALIAS = 'UF_CRM_1572422724116'
    CLIENT_PHONE_ALIAS = 'UF_CRM_1572421180924'
    ORDER_ALIAS = 'UF_CRM_1572513138'

    DEAL_STAGE_ALIAS = 'STAGE_ID'
    DEAL_OPEN_STATUS_ID = 'C3:EXECUTING'
    DEAL_CLOSED_STATUS_ID = 'C3:1'

    TgWorker = None
    get_deals_params = None

    def __init__(self, TGWorker):
        self.TgWorker = TGWorker
        self.get_deals_params = {'filter': {self.COURIER_FIELD_ALIAS: None,
                                            self.DEAL_STAGE_ALIAS: [self.DEAL_OPEN_STATUS_ID,
                                                                    self.DEAL_CLOSED_STATUS_ID]},
                                 'select': [self.DEAL_ID_ALIAS, self.TITLE_ALIAS, self.ORDER_ALIAS,
                                            self.CLIENT_PHONE_ALIAS, self.ADDRESS_ALIAS, self.DEAL_STAGE_ALIAS]}

    def _send_request(self, user, method, params=None, custom_error_text=''):
        if params is None:
            params = {}

        for a in range(self.REQUESTS_MAX_ATTEMPTS):
            try:
                response = self.SESSION.post(url=creds.BITRIX_API_URL + method,
                                             json=params, timeout=self.REQUESTS_TIMEOUT)

                if response:
                    json = response.json()

                    if json['result']:
                        return json
                    else:
                        error = 'Bitrix bad response %s : Attempt: %s, Called: %s : Request params: %s'\
                                % (a, json, custom_error_text, params)
                        logging.error(error)
                else:
                    error = 'Bitrix response failed - %s : Attempt: %s,  Called: %s : Request params: %s'\
                            % (a, response.text, custom_error_text, params)
                    logging.error(error)

            except Exception as e:
                error = 'Sending Bitrix api request %s' % e
                logging.error(error)

        self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.ERROR_BITRIX_REQUEST})
        raise Exception()

    def get_deals_list(self, user):
        try:
            courier_field = self._send_request(user, 'crm.deal.userfield.get', {'id': self.COURIER_FIELD_ID})
            couriers = courier_field['result']['LIST']
            target_courier_id = None

            for c in couriers:
                courier_phone = c['VALUE'].split('/')[-1]
                courier_phone = courier_phone.replace('-', '')
                # simple checking for number format - +7, 7, 8 etc.
                ethalon_pn = user.get_phone_numer()[1:]
                if ethalon_pn in courier_phone:
                    target_courier_id = c['ID']
                    break

            # TODO: don't check courier every query

            if target_courier_id is None:
                return {}

            self.get_deals_params['filter'][self.COURIER_FIELD_ALIAS] = target_courier_id
            deals = self._send_request(user, 'crm.deal.list', self.get_deals_params)

            more_deals = 'next' in deals

            # getting next deal pages, if any
            while more_deals:
                get_next_deals_params = self.get_deals_params.copy()
                get_next_deals_params['start'] = deals['next']
                next_deals = self._send_request(user, 'crm.deal.list', get_next_deals_params)
                deals['result'].extend(next_deals['result'])
                more_deals = 'next' in next_deals

            return deals

        except Exception as e:
            logging.error('Getting deals %s', e)
            self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.ERROR_GETTING_DEALS})
            return None

    def do_deal_action(self, user, deal_id, deal_new_stage):
        try:
            return self._send_request(user, 'crm.deal.update',
                                      {'id': deal_id, 'fields': {self.DEAL_STAGE_ALIAS: deal_new_stage}})
        except Exception as e:
            self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.ERROR_HANDLING_DEAL_ACTION})
            return None
