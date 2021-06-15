from .User import State
from . import creds
from . import TextSnippets as GlobalTxt, config
from . import Commands as Cmd
from . import TelegramWorkerStarter as Starter
from . import BitrixWorker as BW

import source.cmd_handlers.PhotosLoading1.TgHandlers as PhotoLoading1
import source.cmd_handlers.Checklist2.TgHandlers as Checklist2
import source.cmd_handlers.Courier3.TgHandlers as Courier3
import source.cmd_handlers.Florist4.TgHandlers as Florist4
import source.cmd_handlers.FloristOrder5.TgHandlers as FloristOrders5
import source.cmd_handlers.SetAside6.TgHandlers as SetAside6

import logging
import os
import traceback

from telegram.ext import Updater, MessageHandler, Filters, PicklePersistence,\
    ConversationHandler, CommandHandler, CallbackContext

from telegram import ParseMode

from telegram import Update


logger = logging.getLogger(__name__)


def handle_login(update, context):
    user = context.user_data.get(config.USER_PERSISTENT_KEY)
    user.bitrix_login = update.message.text
    update.message.reply_markdown_v2(GlobalTxt.REQUEST_PASSWORD_MESSAGE)
    return State.PASSWORD_REQUESTED


def handle_password(update, context):
    user = context.user_data.get(config.USER_PERSISTENT_KEY)
    user.bitrix_password = update.message.text
    return Starter.restart(update, context)


def error_handler(update, context: CallbackContext):
    try:
        logger.error(msg="Exception while handling Telegram update:", exc_info=context.error)

        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = ''.join(tb_list)

        logger.error(tb_string)

        # don't confuse user with particular error data
        if update:
            # don't confuse user with particular errors data
            update.effective_user.send_message(text=GlobalTxt.UNKNOWN_ERROR, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error(msg="Exception while handling lower-level exception:", exc_info=e)


cv_handler = ConversationHandler(
        entry_points=[CommandHandler([Cmd.START, Cmd.CANCEL], Starter.restart)],
        states={
            State.LOGIN_REQUESTED: [MessageHandler(Filters.text, handle_login)],
            State.PASSWORD_REQUESTED: [MessageHandler(Filters.text, handle_password)],
            State.IN_MENU: [PhotoLoading1.cv_handler,
                            Checklist2.cv_handler,
                            Courier3.cv_handler,
                            Florist4.cv_handler,
                            FloristOrders5.cv_handler,
                            SetAside6.cv_handler]  # all conv handlers here
        },
        fallbacks=[CommandHandler([Cmd.START, Cmd.CANCEL], Starter.restart),
                   MessageHandler(Filters.all, Starter.global_fallback)],
    )


def bitrix_oauth_update_job(context: CallbackContext):
    with BW.OAUTH_LOCK:
        refresh_token = context.bot_data[config.BOT_REFRESH_TOKEN_PERSISTENT_KEY]
        a_token, r_token = BW.refresh_oauth(refresh_token)

        if a_token:
            context.bot_data[config.BOT_ACCESS_TOKEN_PERSISTENT_KEY] = a_token
            context.bot_data[config.BOT_REFRESH_TOKEN_PERSISTENT_KEY] = r_token


# entry point
def run():
    os.makedirs(config.DATA_DIR_NAME, exist_ok=True)
    storage = PicklePersistence(filename=os.path.join(config.DATA_DIR_NAME, config.TG_STORAGE_NAME))

    updater = Updater(creds.TG_BOT_TOKEN, persistence=storage)
    dispatcher = updater.dispatcher

    # handle Bitrix OAuth keys update here in job queue
    bot_data = dispatcher.bot_data
    if config.BOT_ACCESS_TOKEN_PERSISTENT_KEY not in bot_data:
        bot_data[config.BOT_ACCESS_TOKEN_PERSISTENT_KEY] = creds.BITRIX_APP_ACCESS_TOKEN
        bot_data[config.BOT_REFRESH_TOKEN_PERSISTENT_KEY] = creds.BITRIX_APP_REFRESH_TOKEN

    jq = updater.job_queue
    jq.run_repeating(bitrix_oauth_update_job, interval=config.BITRIX_OAUTH_UPDATE_INTERVAL, first=1)

    dispatcher.add_handler(cv_handler)
    for fb in cv_handler.fallbacks:
        dispatcher.add_handler(fb)

    dispatcher.add_error_handler(error_handler)

    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()
