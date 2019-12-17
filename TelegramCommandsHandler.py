import TextSnippets
import Commands
from BitrixWorker import BitrixWorker
import Utils


class TelegramCommandsHandler:
    TgWorker = None
    BitrixWorker = None

    CBQ_DELIM = '_'
    DEALS_BUTTON_PREFIX = 'deals'
    DEALS_BUTTON_PREV_DATA = 'prev'
    DEALS_BUTTON_NEXT_DATA = 'next'
    DEALS_NEXT_CBQ_DATA = DEALS_BUTTON_PREFIX + CBQ_DELIM + DEALS_BUTTON_NEXT_DATA
    DEALS_PREV_CBQ_DATA = DEALS_BUTTON_PREFIX + CBQ_DELIM + DEALS_BUTTON_PREV_DATA
    DEALS_PREV_BUTTON_OBJ = {'text': '<', 'callback_data': DEALS_PREV_CBQ_DATA}
    DEALS_NEXT_BUTTON_OBJ = {'text': '>', 'callback_data': DEALS_NEXT_CBQ_DATA}

    def __init__(self, TelegramWorker):
        self.TgWorker = TelegramWorker
        self.BitrixWorker = BitrixWorker(TelegramWorker)

    def handle_deal_action(self, user, deal_id, deal_action_message):
        chat_id = user.get_chat_id()

        self.TgWorker.delete_message(chat_id, deal_action_message['message_id'])

        deals = user.get_cur_deals()

        if not deals or user.is_cur_deals_outdated():
            self.TgWorker.send_message(user.get_chat_id(),
                                       {'text': TextSnippets.CBQ_DEALS_WRONG_MESSAGE
                                                % Utils.escape_markdown_special_chars(Commands.GET_DEALS_LIST)})
            return

        deal = next((d for d in deals if d[self.BitrixWorker.DEAL_ID_ALIAS] == deal_id), None)

        if deal is None:
            self.TgWorker.send_message(user.get_chat_id(),
                                       {'text': TextSnippets.CBQ_DEALS_WRONG_MESSAGE
                                                % Utils.escape_markdown_special_chars(Commands.GET_DEALS_LIST)})
            return

        new_stage = None
        deal_stage = deal[self.BitrixWorker.DEAL_STAGE_ALIAS]
        if deal_stage == self.BitrixWorker.DEAL_OPEN_STATUS_ID:
            new_stage = self.BitrixWorker.DEAL_CLOSED_STATUS_ID
        elif deal_stage == self.BitrixWorker.DEAL_CLOSED_STATUS_ID:
            new_stage = self.BitrixWorker.DEAL_OPEN_STATUS_ID
        else:
            error = 'Wrong deal stage: %s' % deal_stage
            raise Exception(error)

        result = self.BitrixWorker.do_deal_action(user, deal_id, new_stage)

        if result is not None:
            deal[self.BitrixWorker.DEAL_STAGE_ALIAS] = new_stage
            message_id = user.get_cur_deals_message_id()
            deals_page = user.get_cur_deals()
            deals_msg = self._generate_deals_msg(deals_page, user)
            self.TgWorker.edit_message(chat_id, message_id, deals_msg)

    def get_deals_list(self, user, message):
        deals = self.BitrixWorker.get_deals_list(user)

        if deals is None:
            return

        if not deals:
            self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.YOU_HAVE_NO_DEALS})
            return

        user.set_deals(deals)
        deals_1st_page = user.get_cur_deals()
        deals_msg = self._generate_deals_msg(deals_1st_page, user)

        cur_d_msg_id = user.get_cur_deals_message_id()

        if cur_d_msg_id is not None:
            self.TgWorker.delete_message(user.get_chat_id(), cur_d_msg_id)

        cur_cmd_message_id = user.get_cur_cmd_deals_message_id()

        if cur_cmd_message_id is not None:
            self.TgWorker.delete_message(user.get_chat_id(), cur_cmd_message_id)

        response = self.TgWorker.send_message(user.get_chat_id(), deals_msg)
        user.set_cur_deals_message_id(message, response['result'])

    def handle_command(self, message):
        user_id = message['from']['id']
        chat_id = message['chat']['id']

        if 'text' not in message:
            self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_NONTEXT_COMMAND + '\n' +
                                                         TextSnippets.BOT_HELP_TEXT})
            return

        command = message['text']

        user = self.TgWorker.USERS.get_user(user_id)

        if command == Commands.GET_DEALS_LIST:
            self.get_deals_list(user, message)
        elif command == Commands.HELP:
            self.TgWorker.send_message(chat_id, {'text': TextSnippets.BOT_HELP_EXTENDED_TEXT})
        elif command == Commands.START:
            self.TgWorker.send_message(chat_id, {'text': TextSnippets.BOT_HELP_TEXT})
        elif command == Commands.REAUTHORIZE:
            self.TgWorker.send_message(chat_id, self.TgWorker.REQUEST_PHONE_PARAMS)
            user.unauthorize()
        elif Utils.is_deal_action(command):
            deal_id = command.split(TextSnippets.DEAL_ACTION_DELIM)[1]
            self.handle_deal_action(user, deal_id, message)
        else:
            prepared_msg = Utils.escape_markdown_special_chars(command)
            self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND % prepared_msg + '\n' +
                                                         TextSnippets.BOT_HELP_TEXT})

    def _generate_deals_msg(self, deals, user):
        cur_deals_page_num = user.get_cur_deals_page_num()
        total_deals_pages = user.get_total_deals_pages()
        deals_pages_keyboard = {}

        if total_deals_pages < 2:
            deals_pages_keyboard = {}
        elif cur_deals_page_num == 0:
            deals_pages_keyboard = {'inline_keyboard': [[self.DEALS_NEXT_BUTTON_OBJ]]}
        elif cur_deals_page_num == total_deals_pages - 1:
            deals_pages_keyboard = {'inline_keyboard': [[self.DEALS_PREV_BUTTON_OBJ]]}
        else:
            deals_pages_keyboard = {'inline_keyboard': [[self.DEALS_PREV_BUTTON_OBJ, self.DEALS_NEXT_BUTTON_OBJ]]}

        deals_msg = {'text': TextSnippets.DEAL_HEADER % (user.get_total_deals_num(), cur_deals_page_num + 1,
                                                         total_deals_pages),
                     'reply_markup': deals_pages_keyboard}

        # print 1st page of deals
        for d in deals:
            title = Utils.prepare_external_field(d[self.BitrixWorker.TITLE_ALIAS])
            order = Utils.prepare_external_field(d[self.BitrixWorker.ORDER_ALIAS])

            address = Utils.prepare_external_field(d[self.BitrixWorker.ADDRESS_ALIAS])
            client_phone = Utils.prepare_external_field(d[self.BitrixWorker.CLIENT_PHONE_ALIAS])

            deal_stage = d[self.BitrixWorker.DEAL_STAGE_ALIAS]
            deal_action_command = None
            deal_action_name = None
            deal_id = d[self.BitrixWorker.DEAL_ID_ALIAS]

            if deal_stage == self.BitrixWorker.DEAL_OPEN_STATUS_ID:
                deal_stage = TextSnippets.DEAL_OPEN_STAGE_NAME
                deal_action_name = TextSnippets.DEAL_ACTION_NAME_CLOSE
                deal_action_command = Commands.DEAL_CLOSE_PREFIX + '\\' + TextSnippets.DEAL_ACTION_DELIM + deal_id
            elif deal_stage == self.BitrixWorker.DEAL_CLOSED_STATUS_ID:
                deal_stage = TextSnippets.DEAL_CLOSED_STAGE_NAME
                deal_action_name = TextSnippets.DEAL_ACTION_NAME_OPEN
                deal_action_command = Commands.DEAL_OPEN_PREFIX + '\\' + TextSnippets.DEAL_ACTION_DELIM + deal_id
            else:
                deal_stage = TextSnippets.DEAL_ERROR_STAGE_NAME
                deal_action_name = ''
                deal_action_command = ''

            deals_msg['text'] += (TextSnippets.DEAL_TEMPLATE.format(title, order, address,
                                                                    client_phone, deal_stage,
                                                                    deal_action_name, deal_action_command)
                                  + '\n' + TextSnippets.DEAL_DELIMETER + '\n')

        if total_deals_pages > 1:
            deals_msg['text'] += TextSnippets.DEAL_FOOTER

        return deals_msg

    def handle_deals_pages_cb(self, cbq, cb_data):
        user = self.TgWorker.USERS.get_user(cbq['from']['id'])
        cbq_id = cbq['id']
        deals_page = None
        message = cbq['message']
        message_id = message['message_id']

        if message_id != user.get_cur_deals_message_id():
            self.TgWorker.answer_cbq(cbq_id, TextSnippets.CBQ_DEALS_WRONG_MESSAGE
                                                % Commands.GET_DEALS_LIST, True)
            return

        if cb_data == self.DEALS_BUTTON_NEXT_DATA:
            deals_page = user.get_next_deals()
        elif cb_data == self.DEALS_BUTTON_PREV_DATA:
            deals_page = user.get_prev_deals()
        else:
            self.TgWorker.answer_cbq(cbq_id, TextSnippets.CBQ_UNKNOW_COMMAND, True)
            raise Exception('Handling cb query: unknown cb data %s' % cb_data)

        # page <0 or > total - 1
        if not deals_page:
            return

        deals_msg = self._generate_deals_msg(deals_page, user)

        chat_id = message['chat']['id']

        self.TgWorker.edit_message(chat_id, message_id, deals_msg)
        self.TgWorker.answer_cbq(cbq_id)

    def handle_cb_query(self, cbq):
        # all cbq's are expected in format 'command_data'
        cb_data = cbq['data'].split(self.CBQ_DELIM)
        cb_command = cb_data[0]
        cb_button = cb_data[1]

        if cb_command == self.DEALS_BUTTON_PREFIX:
            self.handle_deals_pages_cb(cbq, cb_button)
        else:
            self.TgWorker.answer_cbq(cbq['id'], TextSnippets.CBQ_UNKNOW_COMMAND, True)
            raise Exception('Handling cb query: unknown cb command %s' % cb_command)
