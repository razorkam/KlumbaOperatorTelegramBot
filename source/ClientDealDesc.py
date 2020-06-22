
class ClientDealDesc:
    address = None
    phone = None
    date = None
    time = None
    sum = None
    photos = []

    def get_dict(self):
        return {
            'address': self.address,
            'phone': self.phone,
            'date': self.date,
            'time': self.time,
            'sum': self.sum,
            'photos': self.photos
        }
