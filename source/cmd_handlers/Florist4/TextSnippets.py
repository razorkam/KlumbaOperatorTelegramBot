from source import Commands as Cmd
from source import TextSnippets as GlobalTxt


FLORIST_TEMPLATE = '*{}*\n*{}*\n\n'
FLORIST_UNKNOWN_ID_TEXT = 'Неизвестный флорист\\. Попробуйте снова\\.\n' + GlobalTxt.SUGGEST_CANCEL_TEXT
FLORIST_SUGGESTION_TEXT = 'Назначьте флориста\\.\n' + GlobalTxt.SUGGEST_CANCEL_TEXT + '\n\n'

FLORIST_SETTING_COMMAND_PATTERN = '^/' + Cmd.SET_FLORIST_PREFIX + '\\' + Cmd.CMD_DELIMETER + r'(\d+)$'

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
