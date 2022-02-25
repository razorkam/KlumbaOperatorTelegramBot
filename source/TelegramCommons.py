from functools import wraps

from telegram.ext import CallbackContext
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, User as TelegramUser, \
    Message as TelegramMessage, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

import source.TextSnippets as GlobalTxt
import source.config as cfg
from source.State import State
from source.BaseUser import BaseUser
import source.StorageWorker as StorageWorker


# decorator for PTB callbacks (update, context: CallbackContext)
# - exposes user variable for fast cached user access from context
# - changes user state to callback result
def tg_callback(func):
    @wraps(func)
    def wrapper(update, context):
        user = context.user_data.get(cfg.USER_PERSISTENT_KEY)

        if update.callback_query:
            update.callback_query.answer()

        state = func(update, context, user)

        if user:
            user.state = state

        return state

    return wrapper


def send_mdv2_reply_keyboard(tg_user: TelegramUser, msg_text, reply_keyboard, one_time_keyboard):
    tg_user.send_message(text=msg_text, parse_mode=ParseMode.MARKDOWN_V2,
                         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=one_time_keyboard))


def send_reply_keyboard_remove(tg_user: TelegramUser, msg_text):
    tg_user.send_message(text=msg_text, parse_mode=ParseMode.MARKDOWN_V2,
                         reply_markup=ReplyKeyboardRemove())


# send message to user with MarkdownV2 formatting and keyboard with cancel/menu button
def send_mdv2(tg_user: TelegramUser, msg_text, inline_keyboard=None):
    msg_text = '\U0001F7E2 \n\n' + msg_text

    cancel_button = InlineKeyboardButton(text=GlobalTxt.CANCEL_BUTTON_TEXT,
                                         callback_data=GlobalTxt.CANCEL_BUTTON_CB_DATA)

    if inline_keyboard:
        inline_keyboard.append([cancel_button])
    else:
        inline_keyboard = [[cancel_button]]

    tg_user.send_message(text=msg_text, parse_mode=ParseMode.MARKDOWN_V2,
                         reply_markup=InlineKeyboardMarkup(inline_keyboard), disable_web_page_preview=True)


# send message to user with MarkdownV2 formatting and keyboard with cancel/menu button
def edit_mdv2(tg_msg: TelegramMessage, msg_text, keyboard=None):
    cancel_button = InlineKeyboardButton(text=GlobalTxt.CANCEL_BUTTON_TEXT,
                                         callback_data=GlobalTxt.CANCEL_BUTTON_CB_DATA)

    if keyboard:
        keyboard.append([cancel_button])
    else:
        keyboard = [[cancel_button]]

    tg_msg.edit_text(text=msg_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=InlineKeyboardMarkup(keyboard),
                     disable_web_page_preview=True)


def send_media_group(tg_user: TelegramUser, media_list):
    tg_user.send_media_group(media_list)


@tg_callback
def restart(update, context: CallbackContext, user):
    auth_button = KeyboardButton(text=GlobalTxt.SEND_CONTACT_BUTTON_TEXT, request_contact=True)

    # has user been already cached?
    if user:
        if StorageWorker.check_authorization(user) and not type(user) is BaseUser:
            return user.restart(update, context)
        else:  # authorization isn't valid now
            send_mdv2_reply_keyboard(update.effective_user, GlobalTxt.AUTHORIZATION_FAILED, [[auth_button]], True)
            return State.LOGIN_REQUESTED

    else:
        send_mdv2_reply_keyboard(update.effective_user, GlobalTxt.REQUEST_LOGIN_MESSAGE, [[auth_button]], True)
        context.user_data[cfg.USER_PERSISTENT_KEY] = BaseUser()
        return State.LOGIN_REQUESTED


@tg_callback
def logout(update, context: CallbackContext, user):
    if cfg.USER_PERSISTENT_KEY in context.user_data:
        del context.user_data[cfg.USER_PERSISTENT_KEY]

    return restart(update, context)


@tg_callback
def global_fallback(update, context: CallbackContext, user):
    send_mdv2(update.effective_user, GlobalTxt.UNKNOWN_COMMAND)
    return user.state if user else None  # don't change actual conversation state
