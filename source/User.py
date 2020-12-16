from enum import Enum
from . import creds
from source.DealData import *


class UserState(Enum):
    PASSWORD_REQUESTED = 1
    AUTHORIZED = 2  # user is in menu - #1
    # flowers photos
    LOADING_PHOTOS = 3

    # checklist loading actions - #2
    CHECKLIST_SETTING_DEAL_NUMBER = 4
    CHECKLIST_SETTING_COURIER = 5
    CHECKLIST_SETTING_PHOTO = 6

    # setting courier on any deal stage - #3
    SETTING_COURIER_DEAL_NUMBER = 7
    SETTING_COURIER_COURIER_CHOOSE = 8


class User:
    def __init__(self):
        self._password = None
        self._state = UserState.PASSWORD_REQUESTED
        self._chat_id = None
        # encoded photos of 'photos' menu step
        self.photos_list = []
        # description of 'checklist' or 'setting courier' menu step
        self.deal_data = DealData()
        self._digest = None

    # pickle serializing fields
    def __getstate__(self):
        return self._chat_id, self._state, self._password

    def __setstate__(self, dump):
        self._chat_id, self._state, self._password = dump
        self.photos_list = []
        self.deal_data = DealData()

    def has_provided_password(self):
        return self._state != UserState.PASSWORD_REQUESTED and self._password == creds.GLOBAL_AUTH_PASSWORD

    def is_in_menu(self):
        return self._state == UserState.AUTHORIZED

    def set_state_menu(self):
        self._state = UserState.AUTHORIZED

    def is_photos_loading(self):
        return self._state == UserState.LOADING_PHOTOS

    def set_state_loading_photos(self):
        self._state = UserState.LOADING_PHOTOS

    def is_checklist_actions_handling(self):
        return self._state in (UserState.CHECKLIST_SETTING_DEAL_NUMBER, UserState.CHECKLIST_SETTING_COURIER,
                               UserState.CHECKLIST_SETTING_PHOTO)

    def is_checklist_deal_number_setting(self):
        return self._state == UserState.CHECKLIST_SETTING_DEAL_NUMBER

    def is_checklist_courier_setting(self):
        return self._state == UserState.CHECKLIST_SETTING_COURIER

    def is_checklist_photo_setting(self):
        return self._state == UserState.CHECKLIST_SETTING_PHOTO

    def is_setting_courier_actions_handling(self):
        return self._state in (UserState.SETTING_COURIER_DEAL_NUMBER, UserState.SETTING_COURIER_COURIER_CHOOSE)

    def is_setting_courier_deal_number_setting(self):
        return self._state == UserState.SETTING_COURIER_DEAL_NUMBER

    def is_setting_courier_courier_choose(self):
        return self._state == UserState.SETTING_COURIER_COURIER_CHOOSE

    def set_state_checklist_setting_deal_number(self):
        self._state = UserState.CHECKLIST_SETTING_DEAL_NUMBER

    def set_state_checklist_setting_courier(self):
        self._state = UserState.CHECKLIST_SETTING_COURIER

    def set_state_checklist_setting_photo(self):
        self._state = UserState.CHECKLIST_SETTING_PHOTO

    def set_state_setting_courier_courier_choose(self):
        self._state = UserState.SETTING_COURIER_COURIER_CHOOSE

    def set_state_setting_courier_deal_number(self):
        self._state = UserState.SETTING_COURIER_DEAL_NUMBER

    def authorize(self, password):
        self._state = UserState.AUTHORIZED
        self._password = password

    def unauthorize(self):
        self._state = UserState.PASSWORD_REQUESTED
        self._password = None
        self._chat_id = None

    def get_password(self):
        return self._password

    def get_chat_id(self):
        return self._chat_id

    def add_deal_photo(self, photo):
        self.photos_list.append(photo)

    def get_deal_photos(self):
        return self.photos_list

    def deal_encode_photos(self):
        for p in self.photos_list:
            p.b64_encode()

        return self.get_deal_photos()

    def clear_deal_photos(self):
        self.photos_list.clear()

    def clear_deal_data(self):
        self.deal_data = DealData()

    def get_state(self):
        return self._state

    def set_digest(self, digest):
        self._digest = digest

    def get_digest(self):
        return self._digest

    def reset_state(self):
        self.clear_deal_data()
        self.clear_deal_photos()
        self.set_state_menu()
