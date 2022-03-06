import logging
import os
from traceback_with_variables import activate_by_import
from telegram import Chat

import source.creds as creds
import source.TextSnippets as GlobalTxt
import source.config as cfg
import source.Commands as Cmd
import source.BitrixWorker as BW

import source.BitrixFieldMappings as BFM
import source.utils.Utils as Utils
import source.TelegramCommons as TgCommons
import source.StorageWorker as StorageWorker
from source.State import State
import source.User as User

import source.cmd_handlers.Equip.TgHandlers as Equip
import source.cmd_handlers.Send.TgHandlers as Send
import source.cmd_handlers.SetCourier.TgHandlers as SetCourier
import source.cmd_handlers.SetFlorist.TgHandlers as SetFlorist
import source.cmd_handlers.FloristOrder.TgHandlers as FloristOrder
import source.cmd_handlers.Reserve.TgHandlers as Reserve
import source.cmd_handlers.Courier.TgHandlers as Courier
import source.festive_approvement.TgHandlers as FestiveApprovement
import source.festive_approvement.Statistics as FestiveStats

from telegram.ext import Updater, MessageHandler, Filters, PicklePersistence, \
    ConversationHandler, CommandHandler, CallbackContext, CallbackQueryHandler

from telegram import Update, KeyboardButton, BotCommand

logger = logging.getLogger(__name__)
JOB_QUEUE = None


@TgCommons.tg_callback
def handle_login(update: Update, context, user):
    auth_button = KeyboardButton(text=GlobalTxt.SEND_CONTACT_BUTTON_TEXT, request_contact=True)
    contact = update.message.contact

    # check that sent contact is user's own contact
    if not contact or contact.user_id != update.effective_user.id:
        TgCommons.send_mdv2_reply_keyboard(update.effective_user, GlobalTxt.AUTHORIZATION_FAILED,
                                           [[auth_button]], True)
        return

    user.phone_number = Utils.prepare_phone_number(contact.phone_number)

    is_authorized = StorageWorker.check_authorization(user)

    if contact.user_id == update.effective_user.id and is_authorized:
        position = BW.get_user_position(user.bitrix_user_id)

        if position == BFM.COURIER_POSITION_ID:
            authorized_user = User.Courier.from_base(user)
        else:
            authorized_user = User.Operator.from_base(user)

        TgCommons.send_reply_keyboard_remove(update.effective_user, GlobalTxt.AUTHORIZATION_SUCCESSFUL)
        context.user_data[cfg.USER_PERSISTENT_KEY] = authorized_user

        return authorized_user.restart(update, context)
    else:
        TgCommons.send_mdv2_reply_keyboard(update.effective_user, GlobalTxt.REQUEST_LOGIN_MESSAGE,
                                           [[auth_button]], True)
        return State.LOGIN_REQUESTED


def error_handler(update, context: CallbackContext):
    try:
        logger.error(msg="Exception while handling Telegram update:", exc_info=context.error)

        # don't confuse user with particular error data
        if update:
            if update.effective_chat.type == Chat.PRIVATE:
                # don't confuse user with particular errors data
                TgCommons.send_mdv2(update.effective_user, GlobalTxt.UNKNOWN_ERROR)
            elif update.effective_chat.type in (Chat.GROUP, Chat.SUPERGROUP):
                TgCommons.send_mdv2_chat(update.effective_chat, GlobalTxt.UNKNOWN_ERROR)
    except Exception as e:
        logger.error(msg="Exception while handling lower-level exception:", exc_info=e)


MENU_HANDLERS = [Equip.cv_handler,
                 Send.cv_handler,
                 SetCourier.cv_handler,
                 SetFlorist.cv_handler,
                 FloristOrder.cv_handler,
                 Reserve.cv_handler]

cv_handler = ConversationHandler(
    entry_points=[CommandHandler([Cmd.START, Cmd.CANCEL, Cmd.LOGOUT], TgCommons.restart,
                                 filters=Filters.chat_type.private),
                  CallbackQueryHandler(callback=TgCommons.restart, pattern=GlobalTxt.CANCEL_BUTTON_CB_DATA),
                  *MENU_HANDLERS,
                  Courier.cv_handler],
    states={
        State.LOGIN_REQUESTED: [MessageHandler(Filters.contact, handle_login)],
        State.IN_OPERATOR_MENU: MENU_HANDLERS,  # all conv handlers here
        State.IN_COURIER_MENU: [Courier.cv_handler]
    },
    fallbacks=[CommandHandler([Cmd.START, Cmd.CANCEL], TgCommons.restart, filters=Filters.chat_type.private),
               CallbackQueryHandler(callback=TgCommons.restart, pattern=GlobalTxt.CANCEL_BUTTON_CB_DATA),
               CommandHandler([Cmd.LOGOUT], TgCommons.logout, filters=Filters.chat_type.private),
               MessageHandler(Filters.chat_type.private & Filters.all, TgCommons.global_fallback),
               CallbackQueryHandler(callback=TgCommons.global_fallback, pattern=GlobalTxt.ANY_STRING_PATTERN)]
)


def bitrix_oauth_update_job(context: CallbackContext):
    with BW.OAUTH_LOCK:
        refresh_token = context.bot_data[cfg.BOT_REFRESH_TOKEN_PERSISTENT_KEY]
        a_token, r_token = BW.refresh_oauth(refresh_token)

        if a_token:
            context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY] = a_token
            context.bot_data[cfg.BOT_REFRESH_TOKEN_PERSISTENT_KEY] = r_token


# entry point
def run():
    os.makedirs(cfg.DATA_DIR_NAME, exist_ok=True)
    storage = PicklePersistence(filename=os.path.join(cfg.DATA_DIR_NAME, cfg.TG_STORAGE_NAME))

    updater = Updater(creds.TG_BOT_TOKEN, persistence=storage)
    dispatcher = updater.dispatcher

    updater.bot.set_my_commands(Cmd.BOT_COMMANDS_LIST)

    # handle Bitrix OAuth keys update here in job queue
    bot_data = dispatcher.bot_data
    if cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY not in bot_data:
        bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY] = creds.BITRIX_APP_ACCESS_TOKEN
        bot_data[cfg.BOT_REFRESH_TOKEN_PERSISTENT_KEY] = creds.BITRIX_APP_REFRESH_TOKEN

    jq = updater.job_queue
    global JOB_QUEUE
    JOB_QUEUE = jq

    # refresh oauth
    jq.run_repeating(bitrix_oauth_update_job, interval=cfg.BITRIX_OAUTH_UPDATE_INTERVAL, first=1)
    # start festive statistics jobs
    FestiveStats.jq_add_festive_stats(jq)

    dispatcher.add_handler(FestiveApprovement.FESTIVE_CV_HANDLER)
    dispatcher.add_handler(FestiveApprovement.FESTIVE_REAPPROVE_HANDLER)
    dispatcher.add_handler(cv_handler)
    for fb in cv_handler.fallbacks:
        dispatcher.add_handler(fb)

    dispatcher.add_error_handler(error_handler)

    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()
