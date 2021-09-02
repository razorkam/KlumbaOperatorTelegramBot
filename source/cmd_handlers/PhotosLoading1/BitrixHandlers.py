import logging

import source.BitrixWorker as BW
import source.utils.Utils as Utils

from source.BitrixFieldsAliases import *
from source.BitrixFieldMappings import *
from source.User import User

logger = logging.getLogger(__name__)


def set_deal_number(user: User, deal_id):
    deal = BW.get_deal(deal_id)

    if not deal:
        return BW.BW_NO_SUCH_DEAL

    user.clear_deal_data()
    user.deal_data.deal_id = deal_id
    user.deal_data.stage = deal.get(DEAL_STAGE_ALIAS)
    user.deal_data.supply_type = deal.get(DEAL_SUPPLY_METHOD_ALIAS)

    has_postcard = Utils.prepare_external_field(deal, DEAL_HAS_POSTCARD_ALIAS)

    if has_postcard == DEAL_HAS_POSTCARD_YES:
        user.deal_data.has_postcard = True
        user.deal_data.postcard_text = Utils.prepare_external_field(deal, DEAL_POSTCARD_TEXT_ALIAS)

    return BW.BW_OK


def update_deal_image(user: User):
    photos_list = user.photos_loading_1.encode_deal_photos()
    deal_data = user.deal_data

    if deal_data.stage not in (DEAL_IS_IN_1C_STAGE, DEAL_IS_IN_UNAPPROVED_STAGE, DEAL_FLORIST_STAGE):
        return BW.BW_WRONG_STAGE

    update_obj = {'id': deal_data.deal_id, 'fields': {DEAL_SMALL_PHOTO_ALIAS: [], DEAL_BIG_PHOTO_ALIAS: [],
                                                      DEAL_STAGE_ALIAS: DEAL_IS_EQUIPPED_STAGE,
                                                      DEAL_CLIENT_URL_ALIAS: user.photos_loading_1.digest}}

    is_takeaway = deal_data.supply_type == DEAL_IS_FOR_TAKEAWAY

    for photo in photos_list:
        update_obj['fields'][DEAL_SMALL_PHOTO_ALIAS].append({'fileData': [photo.name_small,
                                                                          photo.data_small]})
        update_obj['fields'][DEAL_BIG_PHOTO_ALIAS].append({'fileData': [photo.name_big,
                                                                        photo.data_big]})

        logger.info('User %s updating deal %s with photo ids %s:', user.bitrix_login,
                    deal_data.deal_id, photo.name_small)

    # load fake photo to checklist in case of takeaway deal
    if is_takeaway:
        fake_photo = photos_list[0]
        update_obj['fields'][DEAL_CHECKLIST_ALIAS] = {'fileData': [fake_photo.name_small,
                                                                   fake_photo.data_small]}

    result = BW.send_request('crm.deal.update', update_obj)

    if result:
        return BW.BW_OK
    else:
        return BW.BW_INTERNAL_ERROR
