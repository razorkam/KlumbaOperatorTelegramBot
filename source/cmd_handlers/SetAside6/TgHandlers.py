from typing import List
import logging

from telegram.ext import MessageHandler, Filters, CallbackContext, \
    ConversationHandler, CommandHandler

from telegram import PhotoSize

from source.User import State, User, MenuStep, menu_step_entry
import source.Commands as Cmd
import source.config as cfg
import source.TelegramWorkerStarter as Starter
import source.TextSnippets as GlobalTxt
import source.BitrixWorker as GlobalBW

from . import TextSnippets as Txt
from .Photo import Photo as Photo
from . import BitrixHandlers as BitrixHandlers

logger = logging.getLogger(__name__)


@menu_step_entry(MenuStep.SET_ASIDE)
def request_deal_number(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    user.set_aside_6.clear()
    update.message.reply_markdown_v2(Txt.ASK_FOR_DEAL_NUMBER)
    return State.SET_ASIDE_SETTING_DEAL_NUMBER


def set_deal_number(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    deal_id = update.message.text
    deal_info = GlobalBW.get_deal(deal_id)

    if not deal_info:
        update.message.reply_markdown_v2(GlobalTxt.NO_SUCH_DEAL.format(deal_id))
        return None

    user.deal_data.deal_id = deal_id

    update.message.reply_markdown_v2(Txt.ASK_FOR_PHOTO_TEXT)
    return State.SET_ASIDE_LOADING_PHOTOS


def waiting_for_supply(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    result = BitrixHandlers.set_waiting_for_supply(user)

    if result == BitrixHandlers.BH_INTERNAL_ERROR:
        update.message.reply_markdown_v2(GlobalTxt.ERROR_BITRIX_REQUEST)
        return None
    else:  # OK
        update.message.reply_markdown_v2(GlobalTxt.DEAL_UPDATED)
        return Starter.restart(update, context)


def append_photo(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    photos: List[PhotoSize] = update.message.photo

    photo_big = photos[-1]

    unique_id_big = photo_big.file_unique_id
    photo_content_big = photo_big.get_file().download_as_bytearray()
    file_extension_big = photo_big.get_file().file_path.split('.')[-1]

    if photo_content_big:
        # store raw photo data to save it on disk later
        user.set_aside_6.add_deal_photo(Photo(unique_id_big + '_B.' + file_extension_big,
                                              photo_content_big))

        update.message.reply_markdown_v2(Txt.PHOTO_LOADED_TEXT)

        logger.info('User %s uploaded set aside photo %s', user.bitrix_login, unique_id_big)
    else:
        logger.error('No photo content big/small from user %s', user.bitrix_login)


def update_deal_reserve(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    if not user.set_aside_6.photos_list:
        update.message.reply_markdown_v2(Txt.NO_PHOTOS_TEXT)
        return None

    result = BitrixHandlers.update_deal_reserve(user)

    if result == BitrixHandlers.BH_INTERNAL_ERROR:
        update.message.reply_markdown_v2(GlobalTxt.ERROR_BITRIX_REQUEST)
        return None
    else:  # OK
        update.message.reply_markdown_v2(GlobalTxt.DEAL_UPDATED)
        return Starter.restart(update, context)


cv_handler = ConversationHandler(
    entry_points=[CommandHandler(Cmd.SET_ASIDE, request_deal_number)],
    states={
        State.SET_ASIDE_SETTING_DEAL_NUMBER: [MessageHandler(Filters.regex(GlobalTxt.BITRIX_DEAL_NUMBER_PATTERN),
                                                             set_deal_number)],
        State.SET_ASIDE_LOADING_PHOTOS: [CommandHandler(Cmd.WAITING_FOR_SUPPLY, waiting_for_supply),
                                         CommandHandler(Cmd.FINISH, update_deal_reserve),
                                         MessageHandler(Filters.photo, append_photo)],
    },
    fallbacks=[CommandHandler(Cmd.CANCEL, Starter.restart),
               MessageHandler(Filters.all, Starter.global_fallback)],
    map_to_parent={
        State.IN_MENU: State.IN_MENU,
        State.LOGIN_REQUESTED: State.LOGIN_REQUESTED
    }
)
