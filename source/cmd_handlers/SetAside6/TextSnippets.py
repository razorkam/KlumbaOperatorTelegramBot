from source import Commands as Cmd
from source import TextSnippets as GlobalTxt

ASK_FOR_DEAL_NUMBER = 'Введите номер заказа:'
ASK_FOR_PHOTO_TEXT = 'Загрузите одно или несколько фото заказа\\.\n' \
                     'Или используйте /{} для перевода в стадию *Ждет поставки*\n'\
                         .format(Cmd.WAITING_FOR_SUPPLY)\
                     + GlobalTxt.SUGGEST_CANCEL_TEXT

PHOTO_LOADED_TEXT = 'Фото успешно загружено\\.\n' \
                    'Загрузите другие фото, или отмените загрузку, используя /{}\\.\n' \
                    'Используйте /{} для завершения\\.' \
    .format(Cmd.CANCEL, Cmd.FINISH)

NO_PHOTOS_TEXT = 'Нет загруженных фото\\.'
