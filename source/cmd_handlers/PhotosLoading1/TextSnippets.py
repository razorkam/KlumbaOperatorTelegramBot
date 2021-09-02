from source import Commands as Cmd
from source import TextSnippets as GlobalTxt


ASK_FOR_DEAL_NUMBER = 'Введите номер заказа:\n' + GlobalTxt.SUGGEST_CANCEL_TEXT

ASK_FOR_PHOTO_TEXT = 'Загрузите одно или несколько фото\\.\n' + GlobalTxt.SUGGEST_CANCEL_TEXT


FINISH_PHOTO_LOADING = 'Завершить'
FINISH_PHOTO_LOADING_CBQ = 'finish_loading'
FINISH_PHOTO_LOADING_PATTERN = '^' + FINISH_PHOTO_LOADING_CBQ + '$'
FINISH_POSTCARD_LOADING_CBQ = 'finish_postcard_loading'
FINISH_POSTCARD_LOADING_PATTERN = '^' + FINISH_POSTCARD_LOADING_CBQ + '$'

PHOTO_LOADED_TEXT = 'Фото успешно загружено\\.\n' \
                    'Можно загрузить еще фото, или отменить загрузку используя /{}' \
    .format(Cmd.CANCEL)

NO_PHOTOS_TEXT = 'Нет загруженных фото\\. \n'\
                 + GlobalTxt.SUGGEST_CANCEL_TEXT

DEAL_HAS_POSTCARD = 'В заказе есть открытка с текстом: {}\\ \n' \
                    'Загрузите фото открытки\\.\n' + GlobalTxt.SUGGEST_CANCEL_TEXT

PHOTO_LOAD_WRONG_DEAL_STAGE = 'Заказ должен находиться в стадии \'Выбит в 1С\', \'У Флориста\' или \'Несогласовано\' ' \
                              'для перевода в стадию \'Заказ укомплектован\'\\. Измените стадию заказа и попробуйте ' \
                              'снова\\. ' + GlobalTxt.SUGGEST_CANCEL_TEXT
