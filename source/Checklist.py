# storing user checklist ( all data processing while doing checklist setting step)
class Checklist:
    def __init__(self):
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

