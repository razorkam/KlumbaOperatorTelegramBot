import logging

import source.BitrixWorker as BW
import source.utils.Utils as Utils

from source.BitrixFieldsAliases import *
from source.BitrixFieldMappings import *
from source.User import Operator

logger = logging.getLogger(__name__)


def set_deal_number(user: Operator, deal_id):
    deal = BW.get_deal(deal_id)

    if not deal:
        return BW.BW_NO_SUCH_DEAL

    user.deal_data.deal_id = deal_id
    user.deal_data.stage = deal.get(DEAL_STAGE_ALIAS)
    user.deal_data.supply_type = deal.get(DEAL_SUPPLY_METHOD_ALIAS)

    if user.deal_data.stage not in (DEAL_UNAPPROVED_STATUS_ID, DEAL_IS_EQUIPPED_STATUS_ID,
                                    DEAL_FLORIST_STATUS_ID):
        return BW.BW_WRONG_STAGE

    has_postcard = Utils.prepare_external_field(deal, DEAL_HAS_POSTCARD_ALIAS)

    if has_postcard == DEAL_HAS_POSTCARD_YES:
        user.deal_data.has_postcard = True
        user.deal_data.postcard_text = Utils.prepare_external_field(deal, DEAL_POSTCARD_TEXT_ALIAS)

    return BW.BW_OK


def update_deal_image(user: Operator):
    photos_list = user.equip.encode_deal_photos()
    deal_data = user.deal_data

    # switch to previous stage first in case of repeat equip - to trigger robots properly
    if user.equip.repeating:
        BW.update_deal(deal_data.deal_id, {DEAL_STAGE_ALIAS: DEAL_FLORIST_STATUS_ID})

    update_obj = {DEAL_SMALL_PHOTO_ALIAS: [], DEAL_BIG_PHOTO_ALIAS: [],
                  DEAL_STAGE_ALIAS: DEAL_IS_EQUIPPED_STATUS_ID,
                  DEAL_CLIENT_URL_ALIAS: user.equip.digest,
                  DEAL_EQUIPER_ID_ALIAS: user.bitrix_user_id}

    is_takeaway = deal_data.supply_type == DEAL_IS_FOR_TAKEAWAY

    for photo in photos_list:
        update_obj[DEAL_SMALL_PHOTO_ALIAS].append({'fileData': [photo.name_small,
                                                                photo.data_small]})
        update_obj[DEAL_BIG_PHOTO_ALIAS].append({'fileData': [photo.name_big,
                                                              photo.data_big]})

    # load fake photo to checklist in case of takeaway deal
    if is_takeaway:
        fake_photo = photos_list[0]
        update_obj[DEAL_CHECKLIST_ALIAS] = {'fileData': [fake_photo.name_small,
                                                         fake_photo.data_small]}

    postcards_list = user.equip.encode_deal_postcards()
    if postcards_list:
        update_obj[DEAL_POSTCARD_PHOTO_ALIAS] = []
        for photo in postcards_list:
            update_obj[DEAL_POSTCARD_PHOTO_ALIAS].append({'fileData': [photo.name_big,
                                                                       photo.data_big]})

    BW.update_deal(deal_data.deal_id, update_obj)
