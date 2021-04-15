import logging

from telegram.ext import MessageHandler, Filters, CallbackContext, \
    ConversationHandler, CommandHandler

from source.User import State, User, MenuStep, menu_step_entry
import source.Commands as Cmd
import source.config as cfg
import source.Utils as Utils
import source.TelegramWorkerStarter as Starter
import source.TextSnippets as GlobalTxt
import source.BitrixWorker as GlobalBW

from . import TextSnippets as Txt
from . import BitrixHandlers as BitrixHandlers

logger = logging.getLogger(__name__)


@menu_step_entry(MenuStep.FLORIST)
def start(update, context: CallbackContext):
    update.message.reply_markdown_v2(GlobalTxt.ASK_FOR_DEAL_NUMBER_TEXT)
    return State.SETTING_FLORIST_DEAL_NUMBER


def generate_florist_suggestions(user):
    florist_id = user.deal_data.florist_id

    with GlobalBW.FLORISTS_LOCK:
        suggestions = Txt.FLORIST_SUGGESTION_TEXT

        for ck, cv in GlobalBW.FLORISTS.items():
            if florist_id != ck:
                suggestions += Txt.FLORIST_TEMPLATE.format(Utils.escape_mdv2(cv),
                                                           Utils.escape_mdv2(Cmd.CMD_PREFIX + Cmd.SET_FLORIST_PREFIX +
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
        update.message.reply_markdown_v2(GlobalTxt.NO_SUCH_DEAL)
        return None

    user.deal_data = deal_data

    # suggest possible florists
    update.message.reply_markdown_v2(generate_deal_info(user))
    update.message.reply_markdown_v2(generate_florist_suggestions(user))
    logger.info('User %s set florist deal number %s', user.bitrix_login, deal_data.deal_id)

    return State.SETTING_FLORIST_FLORIST_CHOOSE


def florist_setting(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)
    florist_id = context.match.group(1)

    with GlobalBW.FLORISTS_LOCK:
        florist_exists = florist_id in GlobalBW.FLORISTS

    if not florist_exists:
        update.message.reply_markdown_v2(Txt.FLORIST_UNKNOWN_ID_TEXT)
        return None

    user.deal_data.florist_id = florist_id
    result = BitrixHandlers.update_deal_florist(user)

    if result == BitrixHandlers.BH_INTERNAL_ERROR:
        update.message.reply_markdown_v2(GlobalTxt.ERROR_BITRIX_REQUEST)
        return None

    update.message.reply_markdown_v2(GlobalTxt.DEAL_UPDATED)
    logger.info('User id %s set florist %s', user.bitrix_login, florist_id)

    return Starter.restart(update, context)


cv_handler = ConversationHandler(
    entry_points=[CommandHandler(Cmd.FLORIST_SET, start)],
    states={
        State.SETTING_FLORIST_DEAL_NUMBER: [MessageHandler(Filters.regex(GlobalTxt.BITRIX_DEAL_NUMBER_PATTERN),
                                                           deal_number_setting)],
        State.SETTING_FLORIST_FLORIST_CHOOSE: [
            MessageHandler(Filters.regex(Txt.FLORIST_SETTING_COMMAND_PATTERN),
                           florist_setting)]
    },
    fallbacks=[CommandHandler(Cmd.CANCEL, Starter.restart),
               MessageHandler(Filters.all, Starter.global_fallback)],
    map_to_parent={
        State.IN_MENU: State.IN_MENU,
        State.LOGIN_REQUESTED: State.LOGIN_REQUESTED
    }
)
