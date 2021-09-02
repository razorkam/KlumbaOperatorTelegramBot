from typing import List
import logging
import pathlib
import datetime

from telegram.ext import MessageHandler, Filters, CallbackContext, \
    ConversationHandler, CommandHandler, CallbackQueryHandler

from telegram import PhotoSize, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from source.User import State, User, MenuStep, menu_step_entry
import source.Commands as Cmd
import source.config as cfg
import source.TelegramWorkerStarter as Starter
import source.TextSnippets as GlobalTxt
import source.BitrixWorker as GlobalBW
import source.BitrixFieldMappings as BitrixMappings
import source.utils.TelegramCalendar as TgCalendar


from . import TextSnippets as Txt
from .Photo import Photo as Photo
from . import BitrixHandlers as BitrixHandlers

logger = logging.getLogger(__name__)


@menu_step_entry(MenuStep.RESERVE)
def request_deal_number(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    user.reserve6.clear()
    update.message.reply_markdown_v2(Txt.ASK_FOR_DEAL_NUMBER)
    return State.RESERVE_SETTING_DEAL_NUMBER


def set_deal_number(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    deal_id = update.message.text
    deal_info = GlobalBW.get_deal(deal_id)

    if not deal_info:
        update.message.reply_markdown_v2(GlobalTxt.NO_SUCH_DEAL.format(deal_id))
        return None

    user.deal_data.deal_id = deal_id

    buttons = [InlineKeyboardButton(text=Txt.RESERVE_YES_TXT, callback_data=Txt.RESERVE_YES_KEY),
               InlineKeyboardButton(text=Txt.RESERVE_NO_TXT, callback_data=Txt.RESERVE_NO_KEY)]

    update.message.reply_markdown_v2(text=Txt.WILL_YOU_RESERVE, reply_markup=InlineKeyboardMarkup([buttons]))
    return State.RESERVE_WILL_YOU_RESERVE


def reserve_choice(update, context: CallbackContext):
    update.callback_query.answer()
    action = update.callback_query.data

    if action == Txt.RESERVE_YES_KEY:
        update.effective_user.send_message(text=Txt.ASK_FOR_PHOTO_TEXT, parse_mode=ParseMode.MARKDOWN_V2)
        return State.RESERVE_LOADING_PHOTOS
    elif action == Txt.RESERVE_NO_KEY:
        buttons = [InlineKeyboardButton(text=Txt.SWITCH_STAGE_WAITING_FOR_SUPPLY_TXT,
                                        callback_data=Txt.SWITCH_STAGE_WAITING_FOR_SUPPLY_KEY),
                   InlineKeyboardButton(text=Txt.SWITCH_STAGE_PROCESSED_TXT,
                                        callback_data=Txt.SWITCH_STAGE_PROCESSED_KEY)]
        update.effective_user.send_message(text=Txt.SWITCH_STAGE, parse_mode=ParseMode.MARKDOWN_V2,
                                           reply_markup=InlineKeyboardMarkup([buttons]))
        return State.RESERVE_SWITCHING_STAGE


def append_photo(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    photos: List[PhotoSize] = update.message.photo

    photo_big = photos[-1]

    unique_id_big = photo_big.file_unique_id
    photo_content_big = photo_big.get_file().download_as_bytearray()
    file_extension_big = photo_big.get_file().file_path.split('.')[-1]

    if photo_content_big:
        user.reserve6.add_deal_photo(Photo(unique_id_big + '_B.' + file_extension_big,
                                           photo_content_big))

        update.message.reply_markdown_v2(Txt.PHOTO_LOADED_TEXT)

        logger.info('User %s uploaded reserve photo %s', user.bitrix_login, unique_id_big)
    else:
        logger.error('No photo content big/small from user %s', user.bitrix_login)


def request_description(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    if not user.reserve6.photos:
        update.message.reply_markdown_v2(Txt.NO_PHOTOS_TEXT)
        return None

    update.message.reply_markdown_v2(Txt.REQUEST_DESCRIPTION)
    return State.RESERVE_DESCRIPTION


def set_description(update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    user.deal_data.reserve_desc = update.message.text
    user.deal_data.has_reserve = BitrixMappings.DEAL_HAS_RESERVE_YES
    user.deal_data.stage = BitrixMappings.DEAL_RESERVED_STAGE

    result = BitrixHandlers.update_deal_reserve(user)

    if result == BitrixHandlers.BH_INTERNAL_ERROR:
        update.message.reply_markdown_v2(GlobalTxt.ERROR_BITRIX_REQUEST)
        return None
    else:  # OK
        update.message.reply_markdown_v2(GlobalTxt.DEAL_UPDATED)
        user.reserve6.clear()
        return Starter.restart(update, context)


def switch_stage(update, context: CallbackContext):
    update.callback_query.answer()
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    action = update.callback_query.data

    if action == Txt.SWITCH_STAGE_WAITING_FOR_SUPPLY_KEY:
        calendar_markup = TgCalendar.create_calendar()
        update.effective_user.send_message(text=Txt.CALENDAR_DESCRIPTION,
                                           parse_mode=ParseMode.MARKDOWN_V2,
                                           reply_markup=calendar_markup)

        return State.RESERVE_SUPPLY_CALENDAR
    elif action == Txt.SWITCH_STAGE_PROCESSED_KEY:
        user.deal_data.stage = BitrixMappings.DEAL_RESERVED_STAGE
        user.deal_data.reserve_desc = Txt.NO_RESERVE_NEEDED_STUB
        user.deal_data.has_reserve = BitrixMappings.DEAL_HAS_RESERVE_NO
        user.deal_data.supply_datetime = None

        photo_stub_name = 'no_reserve_needed.png'
        photo_stub_path = pathlib.Path(__file__).parent.resolve() / 'data' / photo_stub_name

        with open(photo_stub_path, 'rb') as f:
            stub_bytes = f.read()
            user.reserve6.add_deal_photo(Photo(photo_stub_name,
                                               stub_bytes))

    result = BitrixHandlers.update_deal_reserve(user)

    if result == BitrixHandlers.BH_INTERNAL_ERROR:
        update.effective_user.send_message(text=GlobalTxt.ERROR_BITRIX_REQUEST, parse_mode=ParseMode.MARKDOWN_V2)
        return None
    else:  # OK
        update.effective_user.send_message(text=GlobalTxt.DEAL_UPDATED, parse_mode=ParseMode.MARKDOWN_V2)
        user.reserve6.clear()
        return Starter.restart(update, context)


def calendar_selection(update, context: CallbackContext):
    query = update.callback_query
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    result, dt = TgCalendar.process_calendar_selection(update, context)

    if result:
        if dt < datetime.datetime.now():
            query.answer(text=Txt.DATE_TOO_EARLY)
            context.bot.edit_message_text(text=query.message.text,
                                          chat_id=query.message.chat_id,
                                          message_id=query.message.message_id,
                                          reply_markup=TgCalendar.create_calendar())

            return None

        query.answer()
        user.deal_data.stage = BitrixMappings.DEAL_WAITING_FOR_SUPPLY_STAGE
        user.deal_data.reserve_desc = None
        user.deal_data.supply_datetime = dt.isoformat()
        user.deal_data.has_reserve = BitrixMappings.DEAL_HAS_RESERVE_NO

        res = BitrixHandlers.update_deal_reserve(user)

        if res == BitrixHandlers.BH_INTERNAL_ERROR:
            update.effective_user.send_message(text=GlobalTxt.ERROR_BITRIX_REQUEST, parse_mode=ParseMode.MARKDOWN_V2)
            return None
        else:  # OK
            update.effective_user.send_message(text=GlobalTxt.DEAL_UPDATED, parse_mode=ParseMode.MARKDOWN_V2)
            user.reserve6.clear()
            return Starter.restart(update, context)

    query.answer()


cv_handler = ConversationHandler(
    entry_points=[CommandHandler(Cmd.RESERVE, request_deal_number)],
    states={
        State.RESERVE_SETTING_DEAL_NUMBER: [MessageHandler(Filters.regex(GlobalTxt.BITRIX_DEAL_NUMBER_PATTERN),
                                                           set_deal_number)],
        State.RESERVE_WILL_YOU_RESERVE: [CallbackQueryHandler(callback=reserve_choice,
                                                              pattern=Txt.RESERVE_CB_PATTERN)],
        State.RESERVE_LOADING_PHOTOS: [CommandHandler(Cmd.FINISH, request_description),
                                       MessageHandler(Filters.photo, append_photo)],
        State.RESERVE_DESCRIPTION: [MessageHandler(Filters.text, set_description)],
        State.RESERVE_SWITCHING_STAGE: [CallbackQueryHandler(callback=switch_stage,
                                                             pattern=Txt.SWITCH_STAGE_CB_PATTERN)],
        State.RESERVE_SUPPLY_CALENDAR: [CallbackQueryHandler(callback=calendar_selection,
                                                             pattern=TgCalendar.PATTERN)]
    },
    fallbacks=[CommandHandler(Cmd.CANCEL, Starter.restart),
               MessageHandler(Filters.all, Starter.global_fallback)],
    map_to_parent={
        State.IN_MENU: State.IN_MENU,
        State.LOGIN_REQUESTED: State.LOGIN_REQUESTED
    }
)
