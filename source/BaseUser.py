from source.DealData import DealData
from source.State import State


class BaseUser:
    def __init__(self):
        self.phone_number = None
        self.bitrix_user_id = None
        self.state = State.LOGIN_REQUESTED

        # any deal description
        self.deal_data = DealData()

    def __getstate__(self):
        return {
            'phone_number': self.phone_number,
            'bitrix_user_id': self.bitrix_user_id
        }

    def __setstate__(self, pickled):
        self.__init__()

        self.phone_number = pickled['phone_number']
        self.bitrix_user_id = pickled['bitrix_user_id']

    def _clear_data(self):
        self.deal_data = DealData()

    def restart(self, update, context):
        return State.LOGIN_REQUESTED
