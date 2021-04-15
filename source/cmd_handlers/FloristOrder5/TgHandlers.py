import logging
from undecorated import undecorated

from telegram.ext import MessageHandler, Filters, CallbackContext, \
    ConversationHandler, CommandHandler, CallbackQueryHandler
from telegram import Update, ParseMode, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from source.User import State, User, MenuStep, menu_step_entry
import source.Commands as Cmd
import source.config as cfg
import source.TelegramWorkerStarter as Starter
import source.TextSnippets as GlobalTxt
import source.BitrixWorker as GlobalBW
import source.creds as creds

from . import TextSnippets as Txt
from . import BitrixHandlers as BitrixHandlers

import source.cmd_handlers.PhotosLoading1.TgHandlers as PhotosLoading1

logger = logging.getLogger(__name__)


def switch_deal_helper(user: User, deal, update: Update, deal_text, keyboard, deal_photo_links):
    prev_messages = user.florist_order_5.prev_messages

    # switching to text message
    if not deal.order_reserve:
        if len(prev_messages) > 1:  # mediagroup previous
            for m in prev_messages[:-1]:
                m.delete()

            user.florist_order_5.prev_messages = [prev_messages[-1].edit_text(text=deal_text,
                                                                              parse_mode=ParseMode.MARKDOWN_V2,
                                                                              reply_markup=keyboard)]
        elif prev_messages[0].photo:  # photo previous
            prev_messages[0].delete()
            user.florist_order_5.prev_messages = [
                update.effective_user.send_message(text=deal_text, parse_mode=ParseMode.MARKDOWN_V2,
                                                   reply_markup=keyboard)]
        else:  # text previous
            user.florist_order_5.prev_messages = [prev_messages[0].edit_text(text=deal_text,
                                                                             parse_mode=ParseMode.MARKDOWN_V2,
                                                                             reply_markup=keyboard)]
    elif len(deal.order_reserve) == 1:  # switching to photo message
        if len(prev_messages) > 1:  # mediagroup previous
            for m in prev_messages:
                m.delete()

            user.florist_order_5.prev_messages = [update.effective_user.send_photo(photo=deal_photo_links[0],
                                                                                   caption=deal_text,
                                                                                   parse_mode=ParseMode.MARKDOWN_V2,
                                                                                   reply_markup=keyboard)]
        elif prev_messages[0].photo:  # photo previous
            user.florist_order_5.prev_messages = [
                prev_messages[0].edit_media(media=InputMediaPhoto(media=deal_photo_links[0],
                                                                  caption=deal_text,
                                                                  parse_mode=ParseMode.MARKDOWN_V2),
                                            reply_markup=keyboard)]
        else:  # text previous
            prev_messages[0].delete()
            user.florist_order_5.prev_messages = [
                update.effective_user.send_photo(photo=deal_photo_links[0], caption=deal_text,
                                                 parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)]
    else:  # switching to mediagroup message
        media_list = [InputMediaPhoto(media=el) for el in deal_photo_links]
        for m in prev_messages:
            m.delete()

        user.florist_order_5.prev_messages = update.effective_user.send_media_group(media=media_list)
        # can't use reply_markup sending mediagroup
        user.florist_order_5.prev_messages.append(
            update.effective_user.send_message(text=deal_text, parse_mode=ParseMode.MARKDOWN_V2,
                                               reply_markup=keyboard))


def render_cur_deal(update: Update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)
    cur_deal_index = user.florist_order_5.cur_deal_index
    deals = user.florist_order_5.deals_list

    is_switching_msg = bool(update.callback_query)

    if not deals:
        update.message.reply_markdown_v2(Txt.NO_ORDERS)
        return None

    buttons = []

    if len(deals) > 1:
        buttons.append(InlineKeyboardButton(text=Txt.PREV_ORDER_BUTTON_TEXT, callback_data=Txt.PREV_ORDER_BUTTON_CB))
        buttons.append(InlineKeyboardButton(text=Txt.NEXT_ORDER_BUTTON_TEXT, callback_data=Txt.NEXT_ORDER_BUTTON_CB))

    keyboard = InlineKeyboardMarkup([buttons]) if buttons else None

    d = deals[cur_deal_index]

    with GlobalBW.OAUTH_LOCK:
        access_token = context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY]

        equip_str = Cmd.CMD_PREFIX + Cmd.EQUIP_ORDER_PREFIX + '\\' + Cmd.CMD_DELIMETER + str(d.deal_id)

        deal_text = Txt.ORDER_TEMPLATE.format(cur_deal_index + 1, len(deals), d.deal_id, d.supply_type, d.order,
                                              d.order_comment, d.postcard_text,
                                              d.sum, d.date, d.time, equip_str)

        deal_photos_links = [creds.BITRIX_MAIN_PAGE + el.replace('auth=', 'auth=' + access_token)
                             for el in d.order_reserve]

        prev_messages = user.florist_order_5.prev_messages

        if is_switching_msg:
            return switch_deal_helper(user, d, update, deal_text, keyboard, deal_photos_links)

        if not d.order_reserve:
            prev_messages.append(update.message.reply_markdown_v2(text=deal_text, reply_markup=keyboard))
        elif len(d.order_reserve) == 1:
            prev_messages.append(update.message.reply_photo(photo=deal_photos_links[0], caption=deal_text,
                                                            parse_mode=ParseMode.MARKDOWN_V2,
                                                            reply_markup=keyboard))
        else:  # multiple photos
            media_list = [InputMediaPhoto(media=el) for el in deal_photos_links]

            prev_messages.extend(update.message.reply_media_group(media=media_list))
            # can't use reply_markup sending mediagroup
            prev_messages.append(update.message.reply_markdown_v2(text=deal_text, reply_markup=keyboard))

    return None


@menu_step_entry(MenuStep.FLORIST_ORDERS)
def get_deals(update: Update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)

    BitrixHandlers.process_deals(user)
    render_cur_deal(update, context)

    return State.FLORIST_SELECTING_ORDER


def equip_deal(update: Update, context: CallbackContext):
    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)
    deal_id = context.match.group(1)

    user.deal_data.deal_id = deal_id
    return undecorated(PhotosLoading1.start_loading)(update, context)


def switch_deal(update: Update, context: CallbackContext):
    update.callback_query.answer()

    user: User = context.user_data.get(cfg.USER_PERSISTENT_KEY)
    action = update.callback_query.data
    deals_size = len(user.florist_order_5.deals_list)

    if action == Txt.PREV_ORDER_BUTTON_CB:
        if user.florist_order_5.cur_deal_index == 0:
            user.florist_order_5.cur_deal_index = deals_size - 1
        else:
            user.florist_order_5.cur_deal_index -= 1

    elif action == Txt.NEXT_ORDER_BUTTON_CB:
        user.florist_order_5.cur_deal_index = (user.florist_order_5.cur_deal_index + 1) % deals_size

    return render_cur_deal(update, context)


cv_handler = ConversationHandler(
    entry_points=[CommandHandler(Cmd.FLORIST_ORDERS_LIST, get_deals)],
    states={
        State.FLORIST_SELECTING_ORDER: [MessageHandler(Filters.regex(Txt.EQUIP_ORDER_COMMAND_PATTERN), equip_deal),
                                        CallbackQueryHandler(callback=switch_deal,
                                                             pattern=Txt.SWITCH_ORDER_CB_PATTERN)],
        State.LOADING_PHOTOS: [CommandHandler(Cmd.FINISH, PhotosLoading1.update_deal),
                               MessageHandler(Filters.photo, PhotosLoading1.append_photo)]
    },
    fallbacks=[CommandHandler(Cmd.CANCEL, Starter.restart),
               MessageHandler(Filters.all, Starter.global_fallback)],
    map_to_parent={
        State.IN_MENU: State.IN_MENU,
        State.LOGIN_REQUESTED: State.LOGIN_REQUESTED
    }
)
