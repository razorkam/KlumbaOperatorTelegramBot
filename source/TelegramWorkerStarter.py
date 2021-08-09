from telegram.ext import CallbackContext
from telegram import ParseMode

import source.config as cfg
import source.Commands as cmd
import source.TextSnippets as GlobalTxt
import source.utils.Utils as Utils
import source.StorageWorker as StorageWorker
from source.User import User, State, MenuStep, menu_step_entry


@menu_step_entry(MenuStep.UNSPECIFIED)
def restart(update, context: CallbackContext):
    user = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    # has user been already cached?
    if user:
        if StorageWorker.check_authorization(user):
            update.effective_user.send_message(text=GlobalTxt.MENU_TEXT.format(cmd.RESERVE,
                                                                               cmd.FLORIST_SET,
                                                                               cmd.PHOTO_LOAD,
                                                                               cmd.CHECKLIST_LOAD,
                                                                               Utils.escape_mdv2(cmd.COURIER_SET),
                                                                               Utils.escape_mdv2(cmd.FLORIST_ORDERS_LIST)),
                                               parse_mode=ParseMode.MARKDOWN_V2)

            return State.IN_MENU
        else:  # authorization isn't valid now
            update.effective_user.send_message(text=GlobalTxt.AUTHORIZATION_FAILED, parse_mode=ParseMode.MARKDOWN_V2)
            return State.LOGIN_REQUESTED

    else:
        update.effective_user.send_message(text=GlobalTxt.REQUEST_LOGIN_MESSAGE, parse_mode=ParseMode.MARKDOWN_V2)
        context.user_data[cfg.USER_PERSISTENT_KEY] = User()
        return State.LOGIN_REQUESTED


def global_fallback(update, context: CallbackContext):
    update.effective_user.send_message(text=GlobalTxt.UNKNOWN_COMMAND, parse_mode=ParseMode.MARKDOWN_V2)
    return None  # don't change actual conversation state
