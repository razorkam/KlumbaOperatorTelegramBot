import logging

import source.BitrixWorker as BW
from source.BitrixFieldsAliases import *
from source.BitrixFieldMappings import *
from source.User import User

BH_OK = 0
BH_WRONG_STAGE = 1
BH_INTERNAL_ERROR = 2

logger = logging.getLogger(__name__)


def update_deal_image(user: User, deal):
    photos_list = user.photos_loading_1.encode_deal_photos()

    if deal[DEAL_STAGE_ALIAS] not in (DEAL_IS_IN_1C_STAGE, DEAL_IS_IN_UNAPPROVED_STAGE, DEAL_FLORIST_STAGE):
        return BH_WRONG_STAGE

    update_obj = {'id': deal['ID'], 'fields': {DEAL_SMALL_PHOTO_ALIAS: [], DEAL_BIG_PHOTO_ALIAS: [],
                                               DEAL_STAGE_ALIAS: DEAL_IS_EQUIPPED_STAGE,
                                               DEAL_CLIENT_URL_ALIAS: user.photos_loading_1.digest}}

    is_takeaway = deal[DEAL_SUPPLY_METHOD_ALIAS] == DEAL_IS_FOR_TAKEAWAY

    for photo in photos_list:
        update_obj['fields'][DEAL_SMALL_PHOTO_ALIAS].append({'fileData': [photo.name_small,
                                                                          photo.data_small]})
        update_obj['fields'][DEAL_BIG_PHOTO_ALIAS].append({'fileData': [photo.name_big,
                                                                        photo.data_big]})

        logger.info('User %s updating deal %s with photo ids %s:', user.bitrix_login,
                    deal['ID'], photo.name_small)

    # load fake photo to checklist in case of takeaway deal
    if is_takeaway:
        fake_photo = photos_list[0]
        update_obj['fields'][DEAL_CHECKLIST_ALIAS] = {'fileData': [fake_photo.name_small,
                                                                   fake_photo.data_small]}

    result = BW.send_request('crm.deal.update', update_obj)

    if result:
        return BH_OK
    else:
        return BH_INTERNAL_ERROR

