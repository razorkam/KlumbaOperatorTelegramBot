
class ClientDealDesc:
    address = None
    date = None
    time = None
    sum = None
    to_pay = None
    incognito = None
    flat = None
    photos = []
    agreed = None

    def get_dict(self):
        return {
            'address': self.address,
            'date': self.date,
            'to_pay': self.to_pay,
            'incognito': self.incognito,
            'time': self.time,
            'sum': self.sum,
            'flat': self.flat,
            'photos': self.photos,
            'agreed' : self.agreed
        }
