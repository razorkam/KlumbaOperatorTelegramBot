import source.BitrixWorker as BW
import source.BitrixFieldMappings as BFM
import source.BitrixFieldsAliases as BFA
import source.utils.Utils as Utils
from source.BaseUser import BaseUser


def approve_deal(deal_id):
    update_obj = {
        BFA.FESTIVE_APPROVEMENT_ALIAS: BFM.FESTIVE_APPROVEMENT_YES,
        BFA.FESTIVE_DECLINE_USER_ALIAS: ''
    }
    BW.update_deal(deal_id, update_obj)


def decline_deal(deal_id, comment, user_id):
    update_obj = {
        BFA.FESTIVE_APPROVEMENT_ALIAS: BFM.FESTIVE_APPROVEMENT_NO,
        BFA.FESTIVE_DECLINE_COMMENT_ALIAS: comment,
        BFA.FESTIVE_DECLINE_USER_ALIAS: user_id
    }
    BW.update_deal(deal_id, update_obj)


def get_info(deal_id, user: BaseUser):
    deal = BW.get_deal(deal_id)

    user.festive_data.deal_link = Utils.prepare_external_field(deal, BFA.DEAL_LINK_ALIAS)
    user.festive_data.deal_order = Utils.prepare_external_field(deal, BFA.DEAL_ORDER_ALIAS)

    user.festive_data.deal_user_declined = Utils.prepare_external_field(BW.BITRIX_IDS_USERS, user.bitrix_user_id,
                                                                        BW.BITRIX_USERS_LOCK)


def reapprove_deal(deal_id):
    update_obj = {
        BFA.FESTIVE_APPROVEMENT_ALIAS: None,
        BFA.FESTIVE_DECLINE_COMMENT_ALIAS: None,
        BFA.FESTIVE_DECLINE_USER_ALIAS: None
    }
    BW.update_deal(deal_id, update_obj)
