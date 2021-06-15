from telegram.ext import CallbackContext, ConversationHandler

import source.config as cfg
import source.Commands as cmd
import source.TextSnippets as GlobalTxt
import source.Utils as Utils
import source.StorageWorker as StorageWorker
from source.User import User, State, MenuStep, menu_step_entry


@menu_step_entry(MenuStep.UNSPECIFIED)
def restart(update, context: CallbackContext):
    user = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    # has user been already cached?
    if user:
        if StorageWorker.check_authorization(user):
            update.message.reply_markdown_v2(GlobalTxt.MENU_TEXT.format(cmd.PHOTO_LOAD,
                                                                        cmd.CHECKLIST_LOAD,
                                                                        cmd.COURIER_SET,
                                                                        cmd.FLORIST_SET,
                                                                        Utils.escape_mdv2(cmd.FLORIST_ORDERS_LIST),
                                                                        Utils.escape_mdv2(cmd.SET_ASIDE)))
            return State.IN_MENU
        else:  # authorization isn't valid now
            update.message.reply_markdown_v2(GlobalTxt.AUTHORIZATION_FAILED)
            return State.LOGIN_REQUESTED

    else:
        update.message.reply_markdown_v2(GlobalTxt.REQUEST_LOGIN_MESSAGE)
        context.user_data[cfg.USER_PERSISTENT_KEY] = User()
        return State.LOGIN_REQUESTED


def global_fallback(update, context: CallbackContext):
    update.message.reply_markdown_v2(GlobalTxt.UNKNOWN_COMMAND)
    return None  # don't change actual conversation state
