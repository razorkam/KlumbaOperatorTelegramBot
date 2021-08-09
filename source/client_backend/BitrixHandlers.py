import logging

import source.BitrixWorker as BW
import source.utils.Utils as Utils
from source.BitrixFieldsAliases import *
from source.BitrixFieldMappings import *
from source.client_backend.JsonKeys import *
from source.client_backend.ClientDealDesc import ClientDealDesc
from source.client_backend.ClientTextSnippets import *

logger = logging.getLogger(__name__)


def get_deal_info_for_client(deal_id):
    try:
        deal = BW.get_deal(deal_id)

        if not deal:
            logger.error('Cant get deal info for deal %s', deal_id)
            return None

        stage = deal[DEAL_STAGE_ALIAS]

        deal_desc = ClientDealDesc()
        deal_desc.agreed = (stage != DEAL_IS_EQUIPPED_STAGE)

        address, location = Utils.prepare_deal_address(deal, DEAL_ADDRESS_ALIAS, escape_md=False)
        deal_desc.address = address

        deal_desc.date = Utils.prepare_deal_date(deal, DEAL_DATE_ALIAS, escape_md=False)
        deal_desc.time = Utils.prepare_deal_time(deal, DEAL_TIME_ALIAS, escape_md=False)
        deal_desc.sum = Utils.prepare_external_field(deal, DEAL_TOTAL_SUM_ALIAS, escape_md=False)
        deal_desc.to_pay = Utils.prepare_external_field(deal, DEAL_SUM_ALIAS, escape_md=False)
        deal_desc.flat = Utils.prepare_external_field(deal, DEAL_FLAT_ALIAS, escape_md=False)

        deal_desc.incognito = Utils.prepare_deal_incognito_client(deal, DEAL_INCOGNITO_ALIAS)

    except Exception as e:
        logger.error('Error getting client deal info: %s', e)
        return None

    return deal_desc


def check_deal_stage_before_update(deal_id):
    try:
        deal = BW.get_deal(deal_id)

        if not deal:
            logger.error('Cant get deal info for deal %s', deal_id)
            return None

        stage = deal[DEAL_STAGE_ALIAS]

        return stage == DEAL_IS_EQUIPPED_STAGE

    except Exception as e:
        logging.error("Exception getting contact data, %s", e)
        return None


def update_deal_by_client(deal_id, data):
    try:
        comment = data.get(REQUEST_COMMENT_ALIAS)
        approved = data.get(REQUEST_APPROVED_ALIAS)
        call_me_back = data.get(REQUEST_CALLMEBACK_ALIAS)

        fields = {
            DEAL_CLIENT_COMMENT_ALIAS: comment,
            DEAL_STAGE_ALIAS: DEAL_IS_IN_APPROVED_STAGE if approved else DEAL_IS_IN_UNAPPROVED_STAGE,
            DEAL_CLIENT_CALLMEBACK_ALIAS: call_me_back,
            DEAL_COMMENT_APPROVED_ALIAS: DEAL_COMMENT_APPROVED_STUB if approved else None
        }

        result = BW.update_deal(deal_id, fields)

        if result:
            return True
        else:
            logger.error('Error updating client deal info: %s', result)
            return False

    except Exception as e:
        logger.error('Error updating client deal info: %s', e)
        return False
