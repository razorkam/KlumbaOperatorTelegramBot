# storing user checklist ( all data processing while doing checklist setting step) / setting courier step
class DealData:
    photo_data = None
    photo_name = None
    couriers_dict = {}
    courier_id = None
    deal_id = None
    order = None
    contact = None
    florist = None
    order_received_by = None
    total_sum = None
    payment_type = None
    payment_method = None
    payment_status = None
    prepaid = None
    to_pay = None
    incognito = None
    order_comment = None
    delivery_comment = None

    def __init__(self):
        # checklist data
        self.photo_data = None
        self.photo_name = None

        self.couriers_dict = {}
        self.courier_id = None

        self.deal_id = None
        self.order = None
        self.contact = None
        self.florist = None
        self.order_received_by = None
        self.total_sum = None
        self.payment_type = None
        self.payment_method = None
        self.payment_status = None
        self.prepaid = None
        self.to_pay = None
        self.incognito = None
        self.order_comment = None
        self.delivery_comment = None

