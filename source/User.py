from enum import Enum


class UserState(Enum):
    PHONE_NUMBER_REQUESTED = 1
    AUTHORIZED = 2


class User:
    _DEALS_PER_PAGE = 3
    _total_deals = 0
    _deals = None
    _working_message_id = None
    preauthorize_msg_list = []
    _deal_cur_ptr = None
    _deal_prev_ptr = None

    def __init__(self):
        self._phone_number = None
        self._state = UserState.PHONE_NUMBER_REQUESTED
        self._chat_id = None

    # pickle serializing fields
    def __getstate__(self):
        return self._chat_id, self._state, self._phone_number, self._working_message_id

    def __setstate__(self, dump):
        self._chat_id, self._state, self._phone_number, self._working_message_id = dump

    # add pre-auth message to delete later
    def add_prauth_message(self, message_id):
        self.preauthorize_msg_list.append(message_id)

    # delete all preauth messages from chat, if so
    def get_prauth_messages(self):
        return self.preauthorize_msg_list

    def clear_prauth_messages(self):
        self.preauthorize_msg_list.clear()

    def is_number_requested(self):
        return self._state == UserState.PHONE_NUMBER_REQUESTED

    def is_authorized(self):
        return self._state == UserState.AUTHORIZED

    def authorize(self, phone_number):
        self._state = UserState.AUTHORIZED
        phone_number.replace('+', '')
        self._phone_number = phone_number

    def unauthorize(self):
        self._state = UserState.PHONE_NUMBER_REQUESTED
        self._phone_number = None
        self._chat_id = None

    def get_phone_numer(self):
        return self._phone_number

    def get_chat_id(self):
        return self._chat_id

    def get_deals(self):
        return self._deals

    def get_total_deals_num(self):
        return self._total_deals

    def set_deals(self, deals):
        self._deals = deals
        self._total_deals = len(deals)

    def get_cur_deals(self):
        if self._deals is None:
            return {}

        return self.get_deals()

    def get_wm_id(self):
        return self._working_message_id

    def set_wm_id(self, wm_id):
        self._working_message_id = wm_id
