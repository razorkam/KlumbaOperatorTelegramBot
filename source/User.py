import logging
from functools import wraps

import source.config as cfg
from source.DealData import *
from source.cmd_handlers.PhotosLoading1.UserData import UserData as PhotosLoading1UserData
from source.cmd_handlers.FloristOrder5.UserData import UserData as FloristOrder5UserData
from source.cmd_handlers.SetAside6.UserData import UserData as SetAside6UserData

logger = logging.getLogger(__name__)


class State:
    LOGIN_REQUESTED = 0
    PASSWORD_REQUESTED = 1
    IN_MENU = 2  # user is in menu - #1
    # flowers photos
    LOADING_PHOTOS = 3

    # checklist loading actions - #2
    CHECKLIST_SETTING_DEAL_NUMBER = 4
    CHECKLIST_SETTING_COURIER = 5
    CHECKLIST_SETTING_PHOTO = 6

    # setting courier on any deal stage - #3
    SETTING_COURIER_DEAL_NUMBER = 7
    SETTING_COURIER_COURIER_CHOOSE = 8

    # florist setting - # 4
    SETTING_FLORIST_DEAL_NUMBER = 9
    SETTING_FLORIST_FLORIST_CHOOSE = 10

    # florist operations - # 5
    FLORIST_ORDERS_LISTING = 11
    FLORIST_SELECTING_ORDER = 12

    # set aside order - #6
    SET_ASIDE_SETTING_DEAL_NUMBER = 13
    SET_ASIDE_LOADING_PHOTOS = 14


class MenuStep:
    UNSPECIFIED = 0
    PHOTOS = 1
    CHECKLIST = 2
    COURIER = 3
    FLORIST = 4
    FLORIST_ORDERS = 5
    SET_ASIDE = 6


# setter decorator for Telegram callbacks only [Update, Context]
def menu_step_entry(step: MenuStep):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = args[1].user_data.get(cfg.USER_PERSISTENT_KEY)

            if user:
                user.menu_step = step

            return func(*args, **kwargs)

        return wrapper

    return decorator


class User:
    def __init__(self):
        self.bitrix_login = None
        self.bitrix_password = None
        self.bitrix_user_id = None
        self._state = State.LOGIN_REQUESTED
        # step 1(photo loading data)
        self.photos_loading_1 = PhotosLoading1UserData()
        # step 5(florist orders listing)
        self.florist_order_5 = FloristOrder5UserData()
        # step 6(set aside)
        self.set_aside_6 = SetAside6UserData()

        # description of 'checklist' or 'setting courier' menu step
        self.deal_data = DealData()

        self.menu_step = MenuStep.UNSPECIFIED

    def __getstate__(self):
        return {
            'bitrix_login': self.bitrix_login,
            'bitrix_password': self.bitrix_password,
            'bitrix_user_id': self.bitrix_user_id,
            '_state': self._state,
            'menu_step': self.menu_step
        }

    def __setstate__(self, state):
        self.__init__()
        self.bitrix_login = state['bitrix_login']
        self.bitrix_password = state['bitrix_password']
        self.bitrix_user_id = state['bitrix_user_id']
        self._state = state['_state']
        self.menu_step = state['menu_step']

    def clear_deal_data(self):
        self.deal_data = DealData()
