import logging

import source.BitrixWorker as BW
from source.BitrixFieldsAliases import *
from source.BitrixFieldMappings import *
from source.User import User

BH_OK = 0
BH_WRONG_STAGE = 1
BH_INTERNAL_ERROR = 2

logger = logging.getLogger(__name__)


def update_deal_checklist(user: User):
    update_obj = {'id': user.deal_data.deal_id,
                  'fields': {DEAL_CHECKLIST_ALIAS: {'fileData': [user.deal_data.photo_name,
                                                                 user.deal_data.photo_data]},
                             DEAL_STAGE_ALIAS: DEAL_IS_IN_DELIVERY_STAGE}}

    if user.deal_data.courier_id:
        update_obj['fields'][DEAL_COURIER_ALIAS] = user.deal_data.courier_id

    result = BW.send_request('crm.deal.update', update_obj)

    if result:
        return BH_OK
    else:
        return BH_INTERNAL_ERROR
