import re
from telegram.ext import ConversationHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram import Update, Chat, InlineKeyboardButton

import source.festive_approvement.FestiveCBQ as FestiveCBQ
import source.creds as creds
import source.TelegramCommons as TgCommons
import source.http_server.TextSnippets as HttpTxt
import source.http_server.Jobs as HttpJobs
import source.TextSnippets as GlobalTxt
import source.festive_approvement.TextSnippets as Txt
from source.festive_approvement.State import State
from source.BaseUser import BaseUser
import source.festive_approvement.BitrixHandlers as BH
import source.utils.Utils as Utils
import source.Commands as Cmd
import source.config as cfg
import source.BitrixWorker as BW
import source.BitrixFieldsAliases as BFA
import source.BitrixFieldMappings as BFM


@TgCommons.tg_callback(False)
def festive_decision(update: Update, context, user):
    user.festive_data.clear()

    action = context.match.group(1)
    deal_id = context.match.group(2)

    if action == HttpTxt.FESTIVE_APPROVE_BUTTON_KEY:
        BH.approve_deal(deal_id)
        TgCommons.send_mdv2_chat(update.effective_chat, Txt.APPROVED_HEADER.format(deal_id))
        TgCommons.edit_mdv2(update.effective_message, msg_text=Txt.APPROVED_HEADER.format('')
                                                               + update.effective_message.text_markdown_v2,
                            need_cancel=False)
        return ConversationHandler.END
    elif action == HttpTxt.FESTIVE_DECLINE_BUTTON_KEY:
        user.festive_data.deal_id = deal_id
        user.festive_data.deal_message = update.effective_message

        BH.get_info(deal_id, user)

        msg = Txt.REQUEST_DECLINE_COMMENT.format(deal_id)
        TgCommons.send_mdv2_chat(chat=update.effective_chat, msg_text=msg,
                                 reply_id=update.callback_query.message.message_id)
        return State.WRITING_DECLINE_COMMENT


@TgCommons.tg_callback(False)
def festive_comment(update: Update, context, user: BaseUser):
    comment = update.message.text
    deal_message = user.festive_data.deal_message
    deal_id = user.festive_data.deal_id

    # send message to unapproved chat firstly
    BH.decline_deal(deal_id, comment, user.bitrix_user_id)
    unapproved_chat = Chat(bot=context.bot, id=creds.FESTIVE_UNAPPROVED_CHAT_ID, type=Chat.SUPERGROUP)
    keyboard = [[InlineKeyboardButton(text=Txt.REAPPROVE_BUTTON_TEXT, callback_data=Txt.REAPPROVE_BUTTON_KEY_PREFIX +
                                                                                    Cmd.CMD_DELIMETER + deal_id)]]
    TgCommons.send_mdv2_chat(unapproved_chat, Txt.DECLINED_HEADER.format(deal_id) +
                             Txt.DEAL_DECLINED.format(user.festive_data.deal_link, user.festive_data.deal_order,
                                                      user.festive_data.deal_user_declined, Utils.prepare_str(comment)),
                             keyboard)

    TgCommons.send_mdv2_chat(update.effective_chat, Txt.DECLINED_HEADER.format(deal_id))

    TgCommons.edit_mdv2(deal_message, msg_text=Txt.DECLINED_HEADER.format('')
                                               + deal_message.text_markdown_v2, need_cancel=False)

    return ConversationHandler.END


@TgCommons.tg_callback(False)
def festive_reapprove(update: Update, context, user: BaseUser):
    deal_id = context.match.group(1)
    deal = BW.get_deal(deal_id)

    deal_order = Utils.prepare_external_field(deal, BFA.DEAL_ORDER_ALIAS)
    deal_responsible = Utils.prepare_external_field(deal, BFA.DEAL_ASSIGNED_ALIAS)
    deal_date = Utils.prepare_deal_date(deal, BFA.DEAL_DATE_ALIAS)
    deal_time = Utils.prepare_deal_time(deal, BFA.DEAL_TIME_ALIAS)
    deal_sum = Utils.prepare_external_field(deal, BFA.DEAL_TOTAL_SUM_ALIAS)

    order_received_by_id = deal.get(BFA.DEAL_ORDER_RECEIVED_BY_ALIAS)
    deal_accepted = Utils.prepare_external_field(BW.BITRIX_IDS_USERS, order_received_by_id,
                                                 BW.BITRIX_USERS_LOCK)

    source_id = Utils.prepare_external_field(deal, BFA.DEAL_SOURCE_ID_ALIAS)
    deal_source = Utils.prepare_external_field(BW.SOURCES, source_id, BW.SOURCES_LOCK)

    contact_id = Utils.prepare_external_field(deal, BFA.DEAL_CONTACT_ALIAS)

    contact_data = BW.get_contact_data(contact_id)
    contact_name = contact_data.get(BFA.CONTACT_USER_NAME_ALIAS)
    contact_phone = contact_data.get(BFA.CONTACT_PHONE_ALIAS)
    deal_contact = contact_name + ' ' + contact_phone

    subdivision_id = Utils.prepare_external_field(deal, BFA.DEAL_SUBDIVISION_ALIAS)
    deal_subdivision = Utils.prepare_external_field(BW.SUBDIVISIONS, subdivision_id, BW.SUBDIVISIONS_LOCK)

    deal_has_reserve = Utils.prepare_external_field(deal, BFA.WEBHOOK_HAS_RESERVE_ALIAS)

    if deal_has_reserve == BFM.DEAL_HAS_RESERVE_YES:
        with BW.BITRIX_USERS_LOCK:
            access_token = context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY]
            photo_urls = BW.process_deal_photo_dl_urls(deal, access_token, (BFA.DEAL_ORDER_RESERVE_ALIAS,))
    else:
        photo_urls = None

    BH.reapprove_deal(deal_id)
    HttpJobs.send_festive_deal_message(context.bot, deal_id, deal_order, deal_responsible,
                                       deal_date, deal_time, deal_sum, deal_accepted,
                                       deal_source, deal_contact, deal_subdivision, photo_urls)

    edited_msg = re.sub(re.escape(Txt.DECLINED_HEADER.format(deal_id)), Txt.REAPPROVED_HEADER.format(deal_id),
                        update.effective_message.text_markdown_v2)

    TgCommons.edit_mdv2(update.effective_message, msg_text=edited_msg,
                        need_cancel=False)


@TgCommons.tg_callback(False)
def fallback(update, context, user: BaseUser):
    return None  # do nothing on fallbacks


FESTIVE_CB_HANDLER = FestiveCBQ.FestiveCBQ(callback=festive_decision, pattern=Txt.FESTIVE_ACTION_PATTERN)
FESTIVE_MESSAGE_HANDLER = MessageHandler(Filters.text & Filters.chat(creds.FESTIVE_APPROVAL_CHAT_ID), festive_comment)
FESTIVE_CV_HANDLER = ConversationHandler(entry_points=[FESTIVE_CB_HANDLER],
                                         states={
                                             State.WRITING_DECLINE_COMMENT: [FESTIVE_MESSAGE_HANDLER]
                                         },
                                         fallbacks=[MessageHandler(Filters.all, fallback),
                                                    CallbackQueryHandler(callback=fallback,
                                                                         pattern=GlobalTxt.ANY_STRING_PATTERN)])

FESTIVE_REAPPROVE_HANDLER = FestiveCBQ.FestiveUnapprovedCBQ(callback=festive_reapprove,
                                                            pattern=Txt.FESTIVE_REAPPROVE_PATTERN)
