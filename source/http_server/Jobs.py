from telegram.ext import CallbackContext
from telegram import InputMediaPhoto, ParseMode, Chat, InlineKeyboardButton, CallbackQuery

import source.utils.Utils as Utils
import source.BitrixWorker as BW
import source.config as cfg
import source.creds as creds
import source.TextSnippets as GlobalTxt
import source.http_server.TextSnippets as Txt
import source.BitrixFieldsAliases as BFA
import source.BitrixFieldMappings as BFM
import source.TelegramCommons as TgCommons
import source.Commands as Cmd


def send_festive_deal_message(bot, deal_id, deal_order, deal_responsible,
                              deal_date, deal_time, deal_sum, deal_accepted,
                              deal_source, deal_contact, deal_subdivision, photo_urls):
    deal_message = Txt.DEAL_FESTIVE_PROCESSED_TEMPLATE.format(deal_id, deal_order, deal_responsible,
                                                              deal_date, deal_time, deal_sum, deal_accepted,
                                                              deal_source, deal_contact, deal_subdivision)

    keyboard = [[InlineKeyboardButton(text=Txt.FESTIVE_APPROVE_BUTTON_TEXT,
                                      callback_data=Txt.FESTIVE_APPROVE_BUTTON_KEY
                                                    + Cmd.CMD_DELIMETER + deal_id)],
                [InlineKeyboardButton(text=Txt.FESTIVE_DECLINE_BUTTON_TEXT,
                                      callback_data=Txt.FESTIVE_DECLINE_BUTTON_KEY
                                                    + Cmd.CMD_DELIMETER + deal_id)]]

    chat = Chat(bot=bot, id=creds.FESTIVE_APPROVAL_CHAT_ID, type=Chat.SUPERGROUP)

    # 1024 symbols of caption only, if more -> need a message
    if photo_urls:
        media_list = [InputMediaPhoto(media=el) for el in photo_urls]
        bot.send_media_group(chat_id=creds.FESTIVE_APPROVAL_CHAT_ID, media=media_list)

    TgCommons.send_mdv2_chat(chat, deal_message, keyboard)


def festive_deal_processed(context: CallbackContext):
    query_components = context.job.context
    bot = context.bot

    with BW.OAUTH_LOCK:
        access_token = context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY]

        deal_id = Utils.prepare_external_field(query_components, BFA.WEBHOOK_DEAL_ID_ALIAS)
        deal_order = Utils.prepare_external_field(query_components, BFA.WEBHOOK_DEAL_ORDER_ALIAS)
        deal_responsible = Utils.prepare_external_field(query_components, BFA.WEBHOOK_DEAL_RESPONSIBLE_ALIAS)
        deal_date = Utils.prepare_external_field(query_components, BFA.WEBHOOK_DATE_ALIAS)
        deal_time = Utils.prepare_external_field(query_components, BFA.WEBHOOK_TIME_ALIAS)
        deal_sum = Utils.prepare_external_field(query_components, BFA.WEBHOOK_SUM_ALIAS)
        deal_accepted = Utils.prepare_external_field(query_components, BFA.WEBHOOK_ACCEPTED_ALIAS)
        deal_source = Utils.prepare_external_field(query_components, BFA.WEBHOOK_SOURCE_ALIAS)
        deal_contact = Utils.prepare_external_field(query_components, BFA.WEBHOOK_CONTACT_ALIAS)
        deal_subdivision = Utils.prepare_external_field(query_components, BFA.WEBHOOK_SUBDIVISION_ALIAS)
        deal_has_reserve = Utils.prepare_external_field(query_components, BFA.WEBHOOK_HAS_RESERVE_ALIAS)

        if deal_id != GlobalTxt.FIELD_IS_EMPTY_PLACEHOLDER:
            if deal_has_reserve == BFM.DEAL_HAS_RESERVE_YES:
                photo_urls = BW.get_deal_photo_dl_urls(deal_id, access_token, (BFA.DEAL_ORDER_RESERVE_ALIAS,))
            else:
                photo_urls = None

            send_festive_deal_message(bot, deal_id, deal_order, deal_responsible,
                                      deal_date, deal_time, deal_sum, deal_accepted,
                                      deal_source, deal_contact, deal_subdivision, photo_urls)
