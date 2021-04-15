from typing import List
from .Photo import Photo


class UserData:
    def __init__(self):
        self.photos_list: List[Photo] = []
        self.digest = str()

    def add_deal_photo(self, photo):
        self.photos_list.append(photo)

    def clear_deal_photos(self):
        self.photos_list.clear()

    def encode_deal_photos(self):
        for p in self.photos_list:
            p.b64_encode()

        return self.photos_list
