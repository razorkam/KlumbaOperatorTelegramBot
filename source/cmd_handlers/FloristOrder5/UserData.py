from typing import List
from telegram import Message
from source.DealData import DealData


class UserData:
    def __init__(self):
        self.deals_list: List[DealData] = []
        self.prev_messages: List[Message] = []
        self.cur_deal_index = 0

    def add_deal(self, deal: DealData):
        self.deals_list.append(deal)

    def clear_deals(self):
        self.deals_list.clear()
        self.cur_deal_index = 0
        self.prev_messages.clear()