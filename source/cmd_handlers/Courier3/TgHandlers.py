import logging

from telegram.ext import MessageHandler, Filters, CallbackContext, \
    ConversationHandler, CommandHandler

from source.User import State, User, MenuStep, menu_step_entry
import source.Commands as Cmd
import source.config as cfg
import source.utils.Utils as Utils
import source.TelegramWorkerStarter as Starter
import source.TextSnippets as GlobalTxt
import source.BitrixWorker as GlobalBW

from . import TextSnippets as Txt
from . import BitrixHandlers as BitrixHandlers
from source.cmd_handlers.Checklist2 import TextSnippets as ChecklistTxt

logger = logging.getLogger(__name__)


@menu_step_entry(MenuStep.COURIER)
def start(update, context: CallbackContext):
    update.message.reply_markdown_v2(GlobalTxt.ASK_FOR_DEAL_NUMBER_TEXT)
    return State.SETTING_COURIER_DEAL_NUMBER


def generate_courier_suggestions(user):
    courier_id = user.deal_data.courier_id

    with GlobalBW.COURIERS_LOCK:
        suggestions = Txt.COURIER_SUGGESTION_TEXT

        for ck, cv in GlobalBW.COURIERS.items():
            if courier_id != ck:
                suggestions += Txt.COURIER_TEMPLATE.format(Utils.escape_mdv2(cv),
                                                           Utils.escape_mdv2(Cmd.CMD_PREFIX + Cmd.SET_COURIER_PREFIX +
                                                                             Cmd.CMD_DELIMETER + ck))

        return suggestions


def generate_deal_info(user):
    florist = Utils.prepare_external_field(GlobalBW.FLORISTS, user.deal_data.florist_id, GlobalBW.FLORISTS_LOCK)
    courier = Utils.prepare_external_field(GlobalBW.COURIERS, user.deal_data.courier_id, GlobalBW.COURIERS_LOCK)
    order_type = Utils.prepare_external_field(GlobalBW.ORDERS_TYPES, user.deal_data.order_type_id,
                                              GlobalBW.ORDERS_TYPES_LOCK)

    return Txt.DEAL_INFO_TEMPLATE.format(user.deal_data.deal_id,
                                         user.deal_data.order,
                                         user.deal_data.contact,
                                         florist,
                                         user.deal_data.order_received_by,
                                         user.deal_data.incognito,
                                         user.deal_data.order_comment,
                                         user.deal_data.delivery_comment,
                                         user.deal_data.total_sum,
                                         user.deal_data.payment_type,
                                         user.deal_data.payment_method,
                                         user.deal_data.payment_status,
                                         user.deal_data.prepaid,
                                         user.deal_data.to_pay, courier, order_type)


def deal_number_setting(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    result, deal_data = GlobalBW.process_deal_info(update.message.text, False)

    if result == GlobalBW.BW_NO_SUCH_DEAL:
        update.message.reply_markdown_v2(GlobalTxt.NO_SUCH_DEAL.format(deal_data.deal_id))
        return None

    user.deal_data = deal_data

    # suggest possible couriers
    update.message.reply_markdown_v2(generate_deal_info(user))
    update.message.reply_markdown_v2(generate_courier_suggestions(user))
    logger.info('User %s set courier deal number %s', user.bitrix_login, deal_data.deal_id)

    return State.SETTING_COURIER_COURIER_CHOOSE


def courier_setting(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)
    courier_id = context.match.group(1)

    with GlobalBW.COURIERS_LOCK:
        courier_exists = courier_id in GlobalBW.COURIERS

    if not courier_exists:
        update.message.reply_markdown_v2(Txt.COURIER_UNKNOWN_ID_TEXT)
        return None

    user.deal_data.courier_id = courier_id
    result = BitrixHandlers.update_deal_courier(user)

    if result == BitrixHandlers.BH_INTERNAL_ERROR:
        update.message.reply_markdown_v2(GlobalTxt.ERROR_BITRIX_REQUEST)
        return None

    update.message.reply_markdown_v2(GlobalTxt.DEAL_UPDATED)
    logger.info('User id %s set courier %s', user.bitrix_login, courier_id)

    return Starter.restart(update, context)


cv_handler = ConversationHandler(
    entry_points=[CommandHandler(Cmd.COURIER_SET, start)],
    states={
        State.SETTING_COURIER_DEAL_NUMBER: [MessageHandler(Filters.regex(GlobalTxt.BITRIX_DEAL_NUMBER_PATTERN),
                                                           deal_number_setting)],
        State.SETTING_COURIER_COURIER_CHOOSE: [
            MessageHandler(Filters.regex(ChecklistTxt.COURIER_SETTING_COMMAND_PATTERN),
                           courier_setting)]
    },
    fallbacks=[CommandHandler([Cmd.START, Cmd.CANCEL], Starter.restart),
               MessageHandler(Filters.all, Starter.global_fallback)],
    map_to_parent={
        State.IN_MENU: State.IN_MENU,
        State.LOGIN_REQUESTED: State.LOGIN_REQUESTED
    }
)
