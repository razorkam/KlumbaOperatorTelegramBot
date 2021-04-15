from source import Commands as Cmd
from source import TextSnippets as GlobalTxt


COURIER_TEMPLATE = '*{}*\n*{}*\n\n'
COURIER_UNKNOWN_ID_TEXT = 'Неизвестный курьер\\. Попробуйте снова\n' + GlobalTxt.SUGGEST_CANCEL_TEXT
COURIER_SUGGESTION_TEXT = 'Назначьте курьера\\.\n' + GlobalTxt.SUGGEST_CANCEL_TEXT + '\n\n'

DEAL_INFO_TEMPLATE = '*Заказ №*: {}\n' \
                     '*Что заказано*: {}\n' \
                     '*Контакт*: {}\n' \
                     '*Флорист*: {}\n' \
                     '*Кто принял заказ*: {}\n' \
                     '*Инкогнито*: {}\n' \
                     '*Комментарий к товару*: {}\n' \
                     '*Комментарий по доставке*: {}\n' \
                     '*Сумма заказа общая\\(итоговая\\):* {}\n\n' \
                     '*Тип оплаты*: {}\n' \
                     '*Способ оплаты*: {}\n' \
                     '*Статус оплаты*: {}\n' \
                     '*Предоплата*: {}\n' \
                     '*К оплате*: {}\n' \
                     '*Курьер*: {}\n' \
                     '*Тип заказа*: {}'
