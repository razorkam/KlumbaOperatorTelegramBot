from .BitrixWorker import BitrixWorker
from .BitrixFieldsAliases import *
from .CbqData import *
from . import Utils, Commands
from .Deal import Deal
import copy


class TelegramCommandsHandler:
    TgWorker = None
    BitrixWorker = None

    def __init__(self, TelegramWorker):
        self.TgWorker = TelegramWorker
        self.BitrixWorker = BitrixWorker(TelegramWorker)

    def handle_deal_view_action(self, user, deal_id):
        deals = user.get_cur_deals()
        deal = next((d for d in deals if d.id == deal_id), None)

        if deal is None:
            self.TgWorker.edit_user_wm(user,
                                       {'text': TextSnippets.CBQ_DEALS_WRONG_MESSAGE,
                                        'reply_markup': TO_DEALS_BUTTON_OBJ})
            return

        address_res_link = TextSnippets.ADDRESS_RESOLUTION_LINK + deal.address

        view_obj = {'reply_markup': TO_DEALS_BUTTON_OBJ,
                    'text': TextSnippets.DEAL_TEMPLATE.format(deal.id, deal.order, deal.date, deal.time, deal.comment,
                                                              deal.customer_phone, deal.customer_phone,
                                                              deal.recipient_name, deal.recipient_surname,
                                                              deal.recipient_phone, deal.recipient_phone,
                                                              deal.address, address_res_link, deal.sum,
                                                              deal.close_command)}

        self.TgWorker.edit_user_wm(user, view_obj)

    def handle_deal_closing_dialog(self, user, deal_id):
        dialog_keyboard = copy.deepcopy(CLOSE_DEAL_DIALOG_BUTTON_OBJ)
        dialog_keyboard['inline_keyboard'][0][0]['callback_data'] += CBQ_DELIM + deal_id

        self.TgWorker.edit_user_wm(user,
                                   {'text': TextSnippets.DEAL_CLOSING_DIALOG_TEXT.format(deal_id),
                                    'reply_markup': dialog_keyboard})

    def handle_deal_closing(self, user, deal_id):
        deals = user.get_cur_deals()

        if not deals:
            self.TgWorker.edit_user_wm(user,
                                       {'text': TextSnippets.CBQ_DEALS_WRONG_MESSAGE,
                                        'reply_markup': TO_DEALS_BUTTON_OBJ})
            return

        deal = next((d for d in deals if d.id == deal_id), None)

        if deal is None:
            self.TgWorker.edit_user_wm(user,
                                       {'text': TextSnippets.CBQ_DEALS_WRONG_MESSAGE,
                                        'reply_markup': TO_DEALS_BUTTON_OBJ})
            return

        new_stage = DEAL_CLOSED_STATUS_ID

        result = self.BitrixWorker.change_deal_stage(user, deal_id, new_stage)

        if result is not None:
            self.get_deals_list(user)

    def get_deals_list(self, user, is_callback=False):
        deals = self.BitrixWorker.get_deals_list(user)

        if deals is None:
            return None

        if not deals or ('result' not in deals):
            msg_obj = {'text': TextSnippets.YOU_HAVE_NO_DEALS,
                                                  'reply_markup': REFRESH_DEALS_BUTTON_OBJ}
            if user.get_wm_id() is None:
                return self.TgWorker.send_message(user.get_chat_id(), msg_obj)
            else:
                self.TgWorker.edit_user_wm(user, msg_obj, from_callback=is_callback)

        deals_msg = self._generate_deals_preview_msg(deals, user)

        # in case of no main menu, send deals list first time
        if user.get_wm_id() is None:
            return self.TgWorker.send_message(user.get_chat_id(), deals_msg)
        else:
            self.TgWorker.edit_user_wm(user, deals_msg, from_callback=is_callback)

    def handle_command(self, message):
        user_id = message['from']['id']
        chat_id = message['chat']['id']
        user = self.TgWorker.USERS.get_user(user_id)

        if 'text' not in message:
            # self.TgWorker.edit_user_wm(user, {'text': TextSnippets.UNKNOWN_NONTEXT_COMMAND + '\n' +
            #                                           TextSnippets.BOT_HELP_TEXT,
            #                                   'reply_markup': TO_DEALS_BUTTON_OBJ})

            # self.get_deals_list(user)
            self.TgWorker.delete_message(chat_id, message['message_id'])
            return

        command = message['text']

        # if command == Commands.GET_DEALS_LIST:
        #     self.get_deals_list(user)
        # elif command == Commands.HELP:
        #     self.TgWorker.edit_user_wm(user, {'text': TextSnippets.BOT_HELP_EXTENDED_TEXT,
        #                                       'reply_markup': TO_MAIN_MENU_BUTTON_OBJ})
        if command == Commands.START:
            # self.TgWorker.edit_user_wm(user, {'text': TextSnippets.BOT_HELP_TEXT})
            self.get_deals_list(user)

        # elif command == Commands.REAUTHORIZE:
        #     res = self.TgWorker.send_message(chat_id, self.TgWorker.REQUEST_PHONE_PARAMS)['result']
        #     user.add_prauth_message(res['message_id'])
        #     user.add_prauth_message(user.get_wm_id())
        #     user.unauthorize()
        elif Utils.is_deal_close_action(command):
            deal_id = command.split(TextSnippets.DEAL_ACTION_DELIM)[1]
            self.handle_deal_closing_dialog(user, deal_id)
        elif Utils.is_deal_view_action(command):
            deal_id = command.split(TextSnippets.DEAL_ACTION_DELIM)[1]
            self.handle_deal_view_action(user, deal_id)
        else:
            pass
            # prepared_msg = Utils.escape_markdown_special_chars(command)
            # self.TgWorker.edit_user_wm(user, {'text': TextSnippets.UNKNOWN_COMMAND % prepared_msg + '\n' +
            #                                           TextSnippets.BOT_HELP_TEXT})

            # self.get_deals_list(user)

        self.TgWorker.delete_message(chat_id, message['message_id'])

    def _generate_deals_preview_msg(self, deals, user):
        deals_msg = {'text': TextSnippets.DEAL_HEADER % (len(deals['result'])),
                     'reply_markup': REFRESH_DEALS_BUTTON_OBJ}

        deals_lst = []

        for d in deals['result']:
            deal_id = Utils.prepare_external_field(d, DEAL_ID_ALIAS)
            time = Utils.prepare_deal_time(d, DEAL_TIME_ALIAS)
            comment = Utils.prepare_external_field(d, DEAL_COMMENT_ALIAS)
            incognito = Utils.prepare_deal_incognito(d, DEAL_INCOGNITO_ALIAS)
            flat = Utils.prepare_external_field(d, DEAL_FLAT_ALIAS)
            recipient_phone = Utils.prepare_external_field(d, DEAL_RECIPIENT_PHONE_ALIAS)
            sum = Utils.prepare_external_field(d, DEAL_SUM_ALIAS)
            date = Utils.prepare_deal_date(d, DEAL_DATE_ALIAS)
            order = Utils.prepare_external_field(d, DEAL_ORDER_ALIAS)
            recipient_name = Utils.prepare_external_field(d, DEAL_RECIPIENT_NAME_ALIAS)
            recipient_surname = Utils.prepare_external_field(d, DEAL_RECIPIENT_SURNAME_ALIAS)

            contact_id = Utils.get_field(d, DEAL_CONTACT_ID_ALIAS)
            customer_phone = self.BitrixWorker.get_contact_phone(user, contact_id)

            address, location = Utils.prepare_deal_address(d, DEAL_ADDRESS_ALIAS)

            deal_close_command = Commands.DEAL_CLOSE_PREFIX + '\\' + TextSnippets.DEAL_ACTION_DELIM + deal_id
            deal_view_command = Commands.DEAL_VIEW_PREFIX + '\\' + TextSnippets.DEAL_ACTION_DELIM + deal_id

            address_res_link = TextSnippets.ADDRESS_RESOLUTION_LINK + address

            deals_msg['text'] += (TextSnippets.DEAL_PREVIEW_TEMPLATE.format(deal_view_command,
                                                                            time, comment,
                                                                            incognito, address, address_res_link,
                                                                            flat, recipient_phone, recipient_phone, sum,
                                                                            deal_close_command)
                                  + '\n\n' + TextSnippets.DEAL_DELIMETER + '\n\n')

            deal_obj = Deal()
            deal_obj.id = deal_id
            deal_obj.time = time
            deal_obj.comment = comment
            deal_obj.incognito = incognito
            deal_obj.address = address
            deal_obj.flat = flat
            deal_obj.recipient_phone = recipient_phone
            deal_obj.sum = sum
            deal_obj.date = date
            deal_obj.order = order
            deal_obj.recipient_name = recipient_name
            deal_obj.recipient_surname = recipient_surname
            deal_obj.customer_phone = customer_phone
            deal_obj.close_command = deal_close_command
            deal_obj.address = address
            deal_obj.location = location

            deals_lst.append(deal_obj)

        user.set_deals(deals_lst)
        return deals_msg

    def handle_deals_pages_cb(self, cbq, cb_data):
        user = self.TgWorker.USERS.get_user(cbq['from']['id'])
        cbq_id = cbq['id']
        message = cbq['message']
        message_id = message['message_id']

        if message_id != user.get_cur_deals_message_id():
            self.TgWorker.answer_cbq(cbq_id, TextSnippets.CBQ_DEALS_WRONG_MESSAGE
                                     % Commands.GET_DEALS_LIST, True)
            return

        if cb_data == DEALS_BUTTON_NEXT_DATA:
            deals_page = user.get_next_deals()
        elif cb_data == DEALS_BUTTON_PREV_DATA:
            deals_page = user.get_prev_deals()
        else:
            self.TgWorker.answer_cbq(cbq_id, TextSnippets.CBQ_UNKNOW_COMMAND, True)
            raise Exception('Handling cb query: unknown cb data %s' % cb_data)

        # page <0 or > total - 1
        if not deals_page:
            return

        deals_msg = self._generate_deals_preview_msg(deals_page, user)

        chat_id = message['chat']['id']

        self.TgWorker.edit_message(chat_id, message_id, deals_msg)
        self.TgWorker.answer_cbq(cbq_id)

    def handle_main_menu_cb(self, cbq, user):
        self.TgWorker.edit_user_wm(user, {'text': TextSnippets.BOT_HELP_TEXT})
        self.TgWorker.answer_cbq(cbq['id'])

    def handle_to_deals_cb(self, cbq, user):
        self.get_deals_list(user, True)
        self.TgWorker.answer_cbq(cbq['id'])

    def handle_close_deal_cb(self, cbq, user, deal_id):
        self.handle_deal_closing(user, deal_id)
        self.TgWorker.answer_cbq(cbq['id'])

    def handle_cb_query(self, cbq):
        # all cbq's are expected in format 'command_data'
        cb_command = cbq['data']
        cb_data = None
        user_id = cbq['from']['id']
        user = self.TgWorker.USERS.get_user(user_id)

        if CBQ_DELIM in cb_command:
            splitted = cbq['data'].split(CBQ_DELIM)
            cb_command = splitted[0]
            cb_data = splitted[1]

        if cb_command == TO_MAIN_MENU_CALLBACK_DATA:
            self.handle_main_menu_cb(cbq, user)
        elif cb_command == TO_DEALS_CALLBACK_DATA:
            self.handle_to_deals_cb(cbq, user)
        elif cb_command == CLOSE_DEAL_CALLBACK_PREFIX:
            self.handle_close_deal_cb(cbq, user, cb_data)
        else:
            self.TgWorker.answer_cbq(cbq['id'], TextSnippets.CBQ_UNKNOW_COMMAND, True)
            raise Exception('Handling cb query: unknown cb command %s' % cb_command)
