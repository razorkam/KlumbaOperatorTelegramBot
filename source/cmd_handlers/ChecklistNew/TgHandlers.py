from typing import List
import logging
import base64

from telegram.ext import MessageHandler, Filters, CallbackContext, \
    ConversationHandler, CommandHandler

from telegram import PhotoSize

from source.User import State, User, MenuStep, menu_step_entry
import source.Commands as Cmd
import source.config as cfg
import source.utils.Utils as Utils
import source.TelegramWorkerStarter as Starter
import source.TextSnippets as GlobalTxt
import source.BitrixWorker as GlobalBW

from . import TextSnippets as Txt
from . import BitrixHandlers as BitrixHandlers

logger = logging.getLogger(__name__)


@menu_step_entry(MenuStep.CHECKLIST)
def start(update, context: CallbackContext):
    update.message.reply_markdown_v2(GlobalTxt.ASK_FOR_DEAL_NUMBER_TEXT)
    return State.CHECKLIST_SETTING_DEAL_NUMBER


def generate_courier_suggestions(user):
    courier_id = user.deal_data.courier_id

    with GlobalBW.COURIERS_LOCK:
        if not courier_id:
            suggestions = Txt.COURIER_SUGGESTION_TEXT
        else:
            suggestions = Txt.COURIER_EXISTS_TEXT.format(Utils.prepare_external_field(GlobalBW.COURIERS, courier_id),
                                                         Utils.escape_mdv2(Cmd.CMD_PREFIX + Cmd.SKIP_COURIER_SETTING))

        for ck, cv in GlobalBW.COURIERS.items():
            if courier_id != ck:
                suggestions += Txt.COURIER_TEMPLATE.format(Utils.escape_mdv2(cv),
                                                           Utils.escape_mdv2(Cmd.CMD_PREFIX + Cmd.SET_COURIER_PREFIX +
                                                                             Cmd.CMD_DELIMETER + ck))

        return suggestions


def deal_number_setting(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    result, deal_data = GlobalBW.process_deal_info(update.message.text, True)

    if result == GlobalBW.BW_NO_SUCH_DEAL:
        update.message.reply_markdown_v2(GlobalTxt.NO_SUCH_DEAL.format(deal_data.deal_id))
        return None

    if result == GlobalBW.BW_WRONG_STAGE:
        update.message.reply_markdown_v2(Txt.CHECKLIST_LOAD_WRONG_DEAL_STAGE)
        return None

    user.deal_data = deal_data

    # suggest possible couriers
    update.message.reply_markdown_v2(generate_courier_suggestions(user))
    logger.info('User %s set checklist deal number %s', user.bitrix_login, deal_data.deal_id)

    return State.CHECKLIST_SETTING_COURIER


def generate_photo_require_text(user):
    florist = Utils.prepare_external_field(GlobalBW.FLORISTS, user.deal_data.florist_id, GlobalBW.FLORISTS_LOCK)
    order_type = Utils.prepare_external_field(GlobalBW.ORDERS_TYPES, user.deal_data.order_type_id,
                                              GlobalBW.ORDERS_TYPES_LOCK)

    return Txt.CHECKLIST_PHOTO_REQUIRE_TEMPLATE.format(user.deal_data.deal_id, user.deal_data.order,
                                                       user.deal_data.contact, florist,
                                                       user.deal_data.order_received_by,
                                                       user.deal_data.incognito,
                                                       user.deal_data.order_comment,
                                                       user.deal_data.delivery_comment,
                                                       user.deal_data.total_sum,
                                                       user.deal_data.payment_type,
                                                       user.deal_data.payment_method,
                                                       user.deal_data.payment_status,
                                                       user.deal_data.prepaid, user.deal_data.to_pay, order_type)


def courier_setting(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)
    courier_id = context.match.group(1)

    with GlobalBW.COURIERS_LOCK:
        courier_exists = courier_id in GlobalBW.COURIERS

    if not courier_exists:
        update.message.reply_markdown_v2(Txt.COURIER_UNKNOWN_ID_TEXT)
        return None

    user.deal_data.courier_id = courier_id
    update.message.reply_markdown_v2(generate_photo_require_text(user))

    return State.CHECKLIST_SETTING_PHOTO


def courier_skipping(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    user.deal_data.courier_id = None
    update.message.reply_markdown_v2(generate_photo_require_text(user))
    return State.CHECKLIST_SETTING_PHOTO


def photo_setting(update, context: CallbackContext):
    user = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    photos: List[PhotoSize] = update.message.photo

    photo = photos[-1]
    unique_id = photo.file_unique_id
    photo_content = photo.get_file().download_as_bytearray()
    file_extension = photo.get_file().file_path.split('.')[-1]

    if photo_content and file_extension:
        encoded_data = base64.b64encode(photo_content).decode('ascii')
        user.deal_data.photo_data = encoded_data
        user.deal_data.photo_name = unique_id + '.' + file_extension

        result = BitrixHandlers.update_deal_checklist(user)

        if result == BitrixHandlers.BH_INTERNAL_ERROR:
            update.message.reply_markdown_v2(GlobalTxt.ERROR_BITRIX_REQUEST)
            return None

        update.message.reply_markdown_v2(GlobalTxt.DEAL_UPDATED)
        logger.info('User id %s uploaded checklist %s', update.message.from_user.id, unique_id)
        return Starter.restart(update, context)
    else:
        logger.error('No photo content big/small from user %s', update.message.from_user.id)
        update.message.reply_markdown_v2(GlobalTxt.ERROR_BITRIX_REQUEST)
        return None


cv_handler = ConversationHandler(
    entry_points=[CommandHandler(Cmd.CHECKLIST_LOAD, start)],
    states={
        State.CHECKLIST_SETTING_DEAL_NUMBER: [MessageHandler(Filters.regex(GlobalTxt.BITRIX_DEAL_NUMBER_PATTERN),
                                                             deal_number_setting)],
        State.CHECKLIST_SETTING_COURIER: [MessageHandler(Filters.regex(Txt.COURIER_SETTING_COMMAND_PATTERN),
                                                         courier_setting),
                                          MessageHandler(Filters.regex(Txt.COURIER_SKIPPING_COMMAND_PATTERN),
                                                         courier_skipping)],
        State.CHECKLIST_SETTING_PHOTO: [MessageHandler(Filters.photo, photo_setting)]
    },
    fallbacks=[CommandHandler([Cmd.START, Cmd.CANCEL], Starter.restart),
               MessageHandler(Filters.all, Starter.global_fallback)],
    map_to_parent={
        State.IN_MENU: State.IN_MENU,
        State.LOGIN_REQUESTED: State.LOGIN_REQUESTED
    }
)
