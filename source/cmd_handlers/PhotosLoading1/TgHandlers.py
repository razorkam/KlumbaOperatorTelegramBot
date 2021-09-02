from typing import List
import logging

from telegram.ext import MessageHandler, Filters, CallbackContext, \
    ConversationHandler, CommandHandler, CallbackQueryHandler

from telegram import PhotoSize, InlineKeyboardMarkup, InlineKeyboardButton, Update, ParseMode

from source.User import State, User, MenuStep, menu_step_entry
import source.Commands as Cmd
import source.config as cfg
import source.TelegramWorkerStarter as Starter
import source.TextSnippets as GlobalTxt
import source.BitrixWorker as BW

from . import TextSnippets as Txt
from .Photo import Photo as Photo
from . import BitrixHandlers as BH
from . import StorageHandlers as StorageHandlers
from . import BitrixHandlers as BitrixHandlers

logger = logging.getLogger(__name__)


@menu_step_entry(MenuStep.PHOTOS)
def request_deal_number(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    user.photos_loading_1.clear()
    update.message.reply_markdown_v2(Txt.ASK_FOR_DEAL_NUMBER)
    return State.SETUP_DEAL_NUMBER


def set_deal_number(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)
    deal_id = update.message.text

    result = BH.set_deal_number(user, deal_id)

    if result == BW.BW_NO_SUCH_DEAL:
        update.message.reply_markdown_v2(GlobalTxt.NO_SUCH_DEAL.format(deal_id))
        return None

    update.message.reply_markdown_v2(Txt.ASK_FOR_PHOTO_TEXT)

    user._state = State.SETUP_PHOTOS
    return user._state


def append_photo(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    photos: List[PhotoSize] = update.message.photo

    photo_big = photos[-1]

    if len(photos) > 1:
        photo_small = photos[1]
    else:
        photo_small = photos[0]

    file_id_big = photo_big.file_id
    unique_id_big = photo_big.file_unique_id
    photo_content_big = photo_big.get_file().download_as_bytearray()
    file_extension_big = photo_big.get_file().file_path.split('.')[-1]

    file_extension_small = photo_small.get_file().file_path.split('.')[-1]
    unique_id_small = photo_small.file_unique_id
    photo_content_small = photo_small.get_file().download_as_bytearray()

    if photo_content_big and photo_content_small:
        # store raw photo data to save it on disk later
        user.photos_loading_1.add_deal_photo(Photo(unique_id_small + '_S.' + file_extension_small,
                                                   unique_id_big + '_B.' + file_extension_big,
                                                   photo_content_small,
                                                   photo_content_big, file_id_big))

        if user._state == State.SETUP_POSTCARD:
            cbq = Txt.FINISH_POSTCARD_LOADING_CBQ
        else:
            cbq = Txt.FINISH_PHOTO_LOADING_CBQ

        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text=Txt.FINISH_PHOTO_LOADING,
                                                               callback_data=cbq)]])
        update.message.reply_markdown_v2(text=Txt.PHOTO_LOADED_TEXT, reply_markup=keyboard)

        logger.info('User id %s uploaded photo %s', update.message.from_user.id, unique_id_small)
    else:
        logger.error('No photo content big/small from user %s', update.message.from_user.id)

    return None  # don't change state


def finish_photo_loading(update: Update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)
    update.callback_query.answer()

    if user.deal_data.has_postcard:
        update.effective_user.send_message(text=Txt.DEAL_HAS_POSTCARD.format(user.deal_data.postcard_text),
                                           parse_mode=ParseMode.MARKDOWN_V2)

        user._state = State.SETUP_POSTCARD
        return user._state
    else:
        return update_deal(update, context)


def finish_postcard_loading(update: Update, context: CallbackContext):
    update.callback_query.answer()

    return update_deal(update, context)



def update_deal(update: Update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    if user._state == State.SETUP_POSTCARD:
        cbq = Txt.FINISH_POSTCARD_LOADING_CBQ
    else:
        cbq = Txt.FINISH_PHOTO_LOADING_CBQ

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text=Txt.FINISH_PHOTO_LOADING,
                                                           callback_data=cbq)]])

    if not user.photos_loading_1.photos:
        update.effective_user.send_message(text=Txt.NO_PHOTOS_TEXT, parse_mode=ParseMode.MARKDOWN_V2,
                                           reply_markup=keyboard)
        return None

    saved = StorageHandlers.save_deal(user, user.deal_data.deal_id)

    if not saved:
        update.effective_user.send_message(text=GlobalTxt.UNKNOWN_ERROR, parse_mode=ParseMode.MARKDOWN_V2,
                                           reply_markup=keyboard)
        return None

    result = BitrixHandlers.update_deal_image(user)

    if result == BW.BW_WRONG_STAGE:
        update.effective_user.send_message(text=Txt.PHOTO_LOAD_WRONG_DEAL_STAGE, parse_mode=ParseMode.MARKDOWN_V2,
                                           reply_markup=keyboard)
        return None
    elif result == BW.BW_INTERNAL_ERROR:
        update.effective_user.send_message(text=GlobalTxt.ERROR_BITRIX_REQUEST, parse_mode=ParseMode.MARKDOWN_V2,
                                           reply_markup=keyboard)
        return None
    else:  # OK
        update.effective_user.send_message(text=GlobalTxt.DEAL_UPDATED, parse_mode=ParseMode.MARKDOWN_V2)
        user.photos_loading_1.clear()
        return Starter.restart(update, context)


cv_handler = ConversationHandler(
    entry_points=[CommandHandler(Cmd.PHOTO_LOAD, request_deal_number)],
    states={
        State.SETUP_DEAL_NUMBER: [MessageHandler(Filters.regex(GlobalTxt.BITRIX_DEAL_NUMBER_PATTERN), set_deal_number)],
        State.SETUP_PHOTOS: [MessageHandler(Filters.photo, append_photo),
                             CallbackQueryHandler(callback=finish_photo_loading,
                                                  pattern=Txt.FINISH_PHOTO_LOADING_PATTERN)],
        State.SETUP_POSTCARD: [MessageHandler(Filters.photo, append_photo),
                               CallbackQueryHandler(callback=finish_postcard_loading,
                                                    pattern=Txt.FINISH_POSTCARD_LOADING_PATTERN)]
    },
    fallbacks=[CommandHandler(Cmd.CANCEL, Starter.restart),
               MessageHandler(Filters.all, Starter.global_fallback)],
    map_to_parent={
        State.IN_MENU: State.IN_MENU,
        State.LOGIN_REQUESTED: State.LOGIN_REQUESTED
    }
)
