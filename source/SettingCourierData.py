# storing user checklist ( all data processing while doing Setting courier step)
class SettingCourierData:
    def __init__(self):
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

