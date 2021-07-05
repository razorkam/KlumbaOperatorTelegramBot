from source import Commands as Cmd
from source import TextSnippets as GlobalTxt

ASK_FOR_DEAL_NUMBER = 'Введите номер заказа:'
ASK_FOR_PHOTO_TEXT = 'Загрузите одно или несколько фото резерва\\.\n' \
                     + GlobalTxt.SUGGEST_CANCEL_TEXT

PHOTO_LOADED_TEXT = 'Фото успешно загружено\\.\n' \
                    'Загрузите другие фото, или отмените загрузку, используя /{}\\.\n' \
                    'Используйте /{} для завершения загрузки\\.' \
    .format(Cmd.CANCEL, Cmd.FINISH)

NO_PHOTOS_TEXT = 'Нет загруженных фото резерва\\.'

WILL_YOU_RESERVE = 'Резервируем товар?'
RESERVE_YES_TXT = 'Да'
RESERVE_YES_KEY = 'reserve_yes'
RESERVE_NO_TXT = 'Нет'
RESERVE_NO_KEY = 'reserve_no'
RESERVE_CB_PATTERN = '^' + RESERVE_YES_KEY + '$|^' + RESERVE_NO_KEY + '$'

SWITCH_STAGE = 'Переведите заказ в одну из стадий:'
SWITCH_STAGE_WAITING_FOR_SUPPLY_TXT = 'Ждет поставки'
SWITCH_STAGE_WAITING_FOR_SUPPLY_KEY = 'reserve_waiting_for_supply'
SWITCH_STAGE_PROCESSED_TXT = 'Обработан'
SWITCH_STAGE_PROCESSED_KEY = 'reserve_processed'
SWITCH_STAGE_CB_PATTERN = '^' + SWITCH_STAGE_WAITING_FOR_SUPPLY_KEY + '$|^' + SWITCH_STAGE_PROCESSED_KEY + '$'

REQUEST_DESCRIPTION = 'Введите текстовое описание отложенного:'

NO_RESERVE_NEEDED_STUB = 'Резерв не нужен'



