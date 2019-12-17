from enum import Enum
import math
import time


class UserState(Enum):
    PHONE_NUMBER_REQUESTED = 1
    AUTHORIZED = 2

class User:
    _DEALS_PER_PAGE = 3
    _DEALS_VALID_TIME = 48 * 60 * 60  # TG message may be deleted by bot for 48 hours, sec
    _cur_deals_page_num = 0
    _total_deals = 0
    _total_deals_pages = 0
    _cur_deals_message_id = None
    _cur_get_deals_cmd_message_id = None
    _deals = None
    _cur_deals_message_ts = None

    def __init__(self):
        self._phone_number = None
        self._state = UserState.PHONE_NUMBER_REQUESTED
        self._chat_id = None

    # pickle serializing fields
    def __getstate__(self):
        return self._chat_id, self._state, self._phone_number

    def __setstate__(self, dump):
        self._chat_id, self._state, self._phone_number = dump

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

    def get_cur_deals_page_num(self):
        return self._cur_deals_page_num

    def get_total_deals_pages(self):
        return self._total_deals_pages

    def get_deals_per_page(self):
        return self._DEALS_PER_PAGE

    def set_deals(self, deals):
        self._deals = deals['result']
        self._cur_deals_page_num = 0
        self._total_deals = deals['total']
        self._total_deals_pages = int(math.ceil(self._total_deals / self._DEALS_PER_PAGE))

    def set_cur_deals_message_id(self, cmd, result):
        self._cur_get_deals_cmd_message_id = cmd['message_id']
        self._cur_deals_message_id = result['message_id']
        self._cur_deals_message_ts = result['date']

    def _get_page_deals(self):
        deal_start_idx = self._cur_deals_page_num * self._DEALS_PER_PAGE
        deal_end_idx = (self._cur_deals_page_num + 1) * self._DEALS_PER_PAGE
        return self._deals[deal_start_idx:deal_end_idx]

    def get_cur_deals(self):
        if self._deals is None \
                or self._cur_deals_page_num < 0 \
                or (self._cur_deals_page_num - 1) > self._total_deals_pages:
            return {}

        return self._get_page_deals()

    def get_next_deals(self):
        if self._deals is None \
                or self._cur_deals_page_num >= self._total_deals_pages-1:
            return {}

        self._cur_deals_page_num += 1
        return self._get_page_deals()

    def get_prev_deals(self):
        if self._deals is None \
                or self._cur_deals_page_num <= 0:
            return {}

        self._cur_deals_page_num -= 1
        return self._get_page_deals()

    def get_cur_deals_message_id(self):
        return self._cur_deals_message_id

    def get_cur_cmd_deals_message_id(self):
        return self._cur_get_deals_cmd_message_id

    def is_cur_deals_outdated(self):
        cur_ts = time.time()
        if cur_ts - self._cur_deals_message_ts > User._DEALS_VALID_TIME:
            return True

        return False


