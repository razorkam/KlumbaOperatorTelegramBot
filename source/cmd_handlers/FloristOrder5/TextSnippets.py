from source import Commands as Cmd
from source import TextSnippets as GlobalTxt

NO_ORDERS = 'Нет назначенных заказов\\.\n' + GlobalTxt.SUGGEST_CANCEL_TEXT
RESERVE_POSTFIX = ' фото'


ORDER_TEMPLATE = 'Заказ {} из {}\n' \
                 '*Резерв товара ^*\n' \
                 '*№ заказа*: {}\n' \
                 '*Доставка/Самовывоз*: {}\n' \
                 '*Что заказано*: {}\n' \
                 '*Комментарий к товару*: {}\n' \
                 '*Текст открытки*: {}\n' \
                 '*Сумма*: {}\n' \
                 '*Дата*: {}\n' \
                 '*Время*: {}\n' \
                 '*Укомплектовать:* {}\n\n' + GlobalTxt.SUGGEST_CANCEL_TEXT

EQUIP_ORDER_COMMAND_PATTERN = '^/' + Cmd.EQUIP_ORDER_PREFIX + '\\' + Cmd.CMD_DELIMETER + r'(\d+)$'

PHOTO_LOADED_TEXT = 'Фото успешно загружено\\.\n' \
                    'Используйте /{} для завершения, загрузите другие фото, или отмените загрузку, используя /{}\\.' \
    .format(Cmd.FINISH, Cmd.CANCEL)

NO_PHOTOS_TEXT = 'Загрузите фото перед укомплектованием заказа\\.\n'\
                 + GlobalTxt.SUGGEST_CANCEL_TEXT

NEXT_ORDER_BUTTON_TEXT = '>'
NEXT_ORDER_BUTTON_CB = 'next_order'
PREV_ORDER_BUTTON_TEXT = '<'
PREV_ORDER_BUTTON_CB = 'prev_order'
SWITCH_ORDER_CB_PATTERN = '^' + NEXT_ORDER_BUTTON_CB + '$|^' + PREV_ORDER_BUTTON_CB + '$'

