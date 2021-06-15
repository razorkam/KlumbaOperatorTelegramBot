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
import source.cmd_handlers.FloristOrder5.TextSnippets as FloristOrdersTxt
import source.BitrixWorker as GlobalBW

from . import TextSnippets as Txt
from .Photo import Photo as Photo
from . import StorageHandlers as StorageHandlers
from . import BitrixHandlers as BitrixHandlers

logger = logging.getLogger(__name__)


@menu_step_entry(MenuStep.PHOTOS)
def start_loading(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    user.photos_loading_1.clear_deal_photos()
    update.message.reply_markdown_v2(Txt.ASK_FOR_PHOTO_TEXT)
    return State.LOADING_PHOTOS


def append_photo(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    photos: List[PhotoSize] = update.message.photo

    photo_big = photos[-1]
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

        msg_text = Txt.PHOTO_LOADED_TEXT if user.menu_step == MenuStep.PHOTOS else FloristOrdersTxt.PHOTO_LOADED_TEXT
        update.message.reply_markdown_v2(msg_text)

        logger.info('User id %s uploaded photo %s', update.message.from_user.id, unique_id_small)
    else:
        logger.error('No photo content big/small from user %s', update.message.from_user.id)

    return None  # don't change state


def update_deal(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    if not user.photos_loading_1.photos_list:
        msg_text = Txt.NO_PHOTOS_TEXT if user.menu_step == MenuStep.PHOTOS else FloristOrdersTxt.NO_PHOTOS_TEXT
        update.message.reply_markdown_v2(msg_text)
        return None

    if user.menu_step == MenuStep.PHOTOS:
        deal_id = update.message.text
    else:  # FloristOrder5
        deal_id = user.deal_data.deal_id

    deal_info = GlobalBW.get_deal(deal_id)

    if not deal_info:
        update.message.reply_markdown_v2(GlobalTxt.NO_SUCH_DEAL.format(deal_id))
        return None

    saved = StorageHandlers.save_deal(user, update.message.text)

    if not saved:
        update.message.reply_markdown_v2(GlobalTxt.UNKNOWN_ERROR)
        return None

    result = BitrixHandlers.update_deal_image(user, deal_info)

    if result == BitrixHandlers.BH_WRONG_STAGE:
        update.message.reply_markdown_v2(Txt.PHOTO_LOAD_WRONG_DEAL_STAGE)
        return None
    elif result == BitrixHandlers.BH_INTERNAL_ERROR:
        update.message.reply_markdown_v2(GlobalTxt.ERROR_BITRIX_REQUEST)
        return None
    else:  # OK
        update.message.reply_markdown_v2(GlobalTxt.DEAL_UPDATED)
        return Starter.restart(update, context)


cv_handler = ConversationHandler(
    entry_points=[CommandHandler(Cmd.PHOTO_LOAD, start_loading)],
    states={
        State.LOADING_PHOTOS: [MessageHandler(Filters.regex(GlobalTxt.BITRIX_DEAL_NUMBER_PATTERN), update_deal),
                               MessageHandler(Filters.photo, append_photo)],
    },
    fallbacks=[CommandHandler(Cmd.CANCEL, Starter.restart),
               MessageHandler(Filters.all, Starter.global_fallback)],
    map_to_parent={
        State.IN_MENU: State.IN_MENU,
        State.LOGIN_REQUESTED: State.LOGIN_REQUESTED
    }
)
