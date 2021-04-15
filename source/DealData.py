import typing


# storing deal data while processing intermediate steps
class DealData:
    photo_data = None
    photo_name = None
    courier_id = None
    courier = None
    deal_id = None
    order = None
    contact = None
    order_received_by = None
    sum = None
    total_sum = None
    payment_type = None
    payment_method = None
    payment_status = None
    prepaid = None
    to_pay = None
    incognito = None
    order_comment = None
    delivery_comment = None
    florist_id = None
    order_type_id = None
    supply_type = None  # Доставка \ Самовывоз
    postcard_text = None  # Текст открытки
    time = None  # Дата
    date = None  # Время
    order_reserve = []  # Резерв товара (ссылки на фото)

    def __init__(self):
        self.photo_data = None
        self.photo_name = None

        self.courier_id = None

        self.deal_id = None
        self.order = None
        self.contact = None
        self.order_received_by = None
        self.total_sum = None
        self.sum = None
        self.payment_type = None
        self.payment_method = None
        self.payment_status = None
        self.prepaid = None
        self.to_pay = None
        self.incognito = None
        self.order_comment = None
        self.delivery_comment = None
        self.order_type_id = None
        self.supply_type = None
        self.postcard_text = None
        self.time = None
        self.date = None
        self.order_reserve = []

        self.florist_id = None

