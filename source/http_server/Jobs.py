from telegram.ext import CallbackContext

import source.utils.Utils as Utils
import source.BitrixWorker as BW
import source.config as cfg
import source.BitrixFieldsAliases as BFM


def deal_equipped(context: CallbackContext):
    query_components = context.job.context
    bot = context.bot

    with BW.OAUTH_LOCK:
        access_token = context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY]

        deal_id = Utils.prepare_external_field(query_components, BFM.WEBHOOK_DEAL_ID_ALIAS)
        deal_order = Utils.prepare_external_field(query_components, BFM.WEBHOOK_DEAL_ORDER_ALIAS)
        deal_responsible = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_RESPONSIBLE_ALIAS)
        deal_florist = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_FLORIST_ALIAS)

        deal_courier = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_COURIER_ALIAS)
        deal_accepted = Utils.prepare_external_field(query_components, WEBHOOK_ACCEPTED_ALIAS)
        deal_sum = Utils.prepare_external_field(query_components, WEBHOOK_SUM_ALIAS)
        deal_date = Utils.prepare_external_field(query_components, WEBHOOK_DATE_ALIAS)
        deal_time = Utils.prepare_external_field(query_components, WEBHOOK_TIME_ALIAS)
        deal_type = Utils.prepare_external_field(query_components, WEBHOOK_TYPE_ALIAS)

        deal_message = Txt.DEAL_TEMPLATE.format(Txt.DEAL_STATE_EQUIPPED, deal_id,
                                                deal_order, deal_courier,
                                                deal_responsible, deal_florist, deal_accepted,
                                                deal_sum, deal_date, deal_time, deal_type)

        if deal_id != Txt.FIELD_IS_EMPTY_PLACEHOLDER:
            photo_urls = BW.get_deal_photo_dl_urls(deal_id, access_token,
                                                   (DEAL_BIG_PHOTO_ALIAS,))

            # 1024 symbols of caption only, if more -> need a message
            if photo_urls:
                media_list = [InputMediaPhoto(media=el) for el in photo_urls]
                media_list[0].caption = deal_message
                media_list[0].parse_mode = ParseMode.MARKDOWN_V2

                bot.send_media_group(chat_id=creds.EQUIPPED_GROUP_CHAT_ID, media=media_list)
            else:
                bot.send_message(chat_id=creds.EQUIPPED_GROUP_CHAT_ID, text=deal_message,
                                 parse_mode=ParseMode.MARKDOWN_V2)
