from source import Commands as Cmd
from source import TextSnippets as GlobalTxt

ASK_FOR_PHOTO_TEXT = 'Загрузите одно или несколько фото заказа\\.\n' + GlobalTxt.SUGGEST_CANCEL_TEXT

PHOTO_LOADED_TEXT = 'Фото успешно загружено\\.\n' \
                    'Введите номер заказа для прикрепления, загрузите другие фото, или отмените загрузку, используя /{}' \
    .format(Cmd.CANCEL)

NO_PHOTOS_TEXT = 'Загрузите фото перед указанием номера заказа\\. \n'\
                 + GlobalTxt.SUGGEST_CANCEL_TEXT

PHOTO_LOAD_WRONG_DEAL_STAGE = 'Заказ должен находиться в стадии \'Выбит в 1С\', \'У Флориста\' или \'Несогласовано\' ' \
                              'для перевода в стадию \'Заказ укомплектован\'\\. Измените стадию заказа и попробуйте ' \
                              'снова\\. ' + GlobalTxt.SUGGEST_CANCEL_TEXT
