import source.config as cfg

from enum import Enum, auto
from typing import Dict
from datetime import datetime
from source.DealData import DealData


# use hardcoded deals per page number to simplify logic for now
DEALS_PER_PAGE = 3


# maintain separate deals type (current user state sometimes can't be different when list rendering needed)
class DealsType(Enum):
    DELIVERS_TODAY = auto()
    DELIVERS_TOMORROW = auto()
    IN_ADVANCE = auto()
    FINISHED_IN_TIME = auto()
    FINISHED_LATE = auto()


class UserData:
    def __init__(self):
        self.deals_dict: Dict[str, DealData] = {}
        self.deals_type = DealsType.DELIVERS_TODAY
        # to get deals for specific date
        self.deals_date: datetime = datetime.now(tz=cfg.TIMEZONE)
        self.page_number = 0
        self.total_pages = 0
        self.late_reason = None
        self.warehouse_return_reason = None

    def add_deal(self, deal: DealData):
        self.deals_dict[deal.deal_id] = deal

    def clear_deals(self):
        self.deals_dict.clear()

    def get_deals_list(self):
        return list(self.deals_dict.values())

    def get_deal(self, deal_id):
        return self.deals_dict[deal_id]

    def clear(self):
        self.deals_dict.clear()
        self.deals_type = DealsType.DELIVERS_TODAY
        self.deals_date = datetime.now(tz=cfg.TIMEZONE)
        self.page_number = 0
        self.total_pages = 0
        self.late_reason = None
        self.warehouse_return_reason = None
