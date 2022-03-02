from source import Commands as Cmd


ASK_FOR_DEAL_NUMBER = 'Введите номер заказа:'
ASK_FOR_PHOTO_TEXT = 'Загрузите одно или несколько фото заказа\\.'
APPROVE_ALREADY_EQUIPPED_DEAL_TXT = 'Заказ {} уже укомплектован\\.\n' \
                                    'Укомплектовать повторно?'
EQUIP_REPEATEDLY_BUTTON_TEXT = 'Да'
EQUIP_REPEATEDLY_BUTTON_CB = 'equip_repeatedly'


FINISH_PHOTO_LOADING = 'Завершить'
FINISH_PHOTO_LOADING_CB = 'finish_loading'

PHOTO_LOADED_TEXT = 'Фото успешно загружено\\.\n' \
                    'Можно загрузить еще фото или завершить загрузку' \
    .format(Cmd.CANCEL)

NO_PHOTOS_TEXT = 'Нет загруженных фото\\.\n'

DEAL_HAS_POSTCARD = 'В заказе есть открытка с текстом: *{}*\\ \n' \
                    'Загрузите фото *лицевой стороны* открытки\\.'

DEAL_REQUEST_POSTCARD_REVERSE_SIDE = 'Загрузите фото стороны открытки, *где виден текст*\\.'

WRONG_DEAL_STAGE = 'Заказ должен находиться в одной из стадий: ' \
                   '*У Флориста*, *Согласовано*, *Несогласовано*\n'\
                   'Измените стадию заказа и попробуйте снова\\.'
