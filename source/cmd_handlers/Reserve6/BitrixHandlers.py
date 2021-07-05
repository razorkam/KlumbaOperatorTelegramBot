import logging

import source.BitrixWorker as BW
from source.BitrixFieldsAliases import *
from source.User import User

BH_OK = 0
BH_WRONG_STAGE = 1
BH_INTERNAL_ERROR = 2

logger = logging.getLogger(__name__)


def update_deal_reserve(user: User):
    deal_id = user.deal_data.deal_id
    photos_list = user.reserve6.encode_deal_photos()

    update_obj = {'id': deal_id, 'fields': {DEAL_ORDER_RESERVE_ALIAS: [],
                                            DEAL_STAGE_ALIAS: user.deal_data.stage,
                                            DEAL_ORDER_RESERVE_DESC_ALIAS: user.deal_data.reserve_desc,
                                            DEAL_ORDER_HAS_RESERVE_ALIAS: user.deal_data.has_reserve}}

    for photo in photos_list:
        update_obj['fields'][DEAL_ORDER_RESERVE_ALIAS].append({'fileData': [photo.name_big,
                                                                            photo.data_big]})

        logger.info('User %s updating deal %s with reserve photo ids %s:', user.bitrix_login,
                    deal_id, photo.name_big)

    result = BW.send_request('crm.deal.update', update_obj)

    if result:
        return BH_OK
    else:
        return BH_INTERNAL_ERROR
