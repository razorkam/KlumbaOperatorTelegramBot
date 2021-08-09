from source import Commands as Cmd
from source import TextSnippets as GlobalTxt

CHECKLIST_LOAD_WRONG_DEAL_STAGE = 'Заказ должен находиться в стадии \'Согласовано\' для перевода в стадию \'В ' \
                                  'доставке\'\\.\n' + GlobalTxt.SUGGEST_CANCEL_TEXT

COURIER_TEMPLATE = '*{}*\n*{}*\n\n'
COURIER_UNKNOWN_ID_TEXT = 'Неизвестный курьер\\. Попробуйте снова\\.\n' + GlobalTxt.SUGGEST_CANCEL_TEXT
COURIER_EXISTS_TEXT = 'Курьер *{}* уже назначен для этого заказа\\.\n' \
                      'Используйте {}, чтобы продолжить без изменения, или назначьте нового курьера\\.\n' \
                      + GlobalTxt.SUGGEST_CANCEL_TEXT + '\n\n'
COURIER_SUGGESTION_TEXT = 'Назначьте курьера\\.\n' + GlobalTxt.SUGGEST_CANCEL_TEXT + '\n\n'

COURIER_SETTING_COMMAND_PATTERN = '^/' + Cmd.SET_COURIER_PREFIX + '\\' + Cmd.CMD_DELIMETER + r'(\d+)$'
COURIER_SKIPPING_COMMAND_PATTERN = '^/' + Cmd.SKIP_COURIER_SETTING + '$'

CHECKLIST_PHOTO_REQUIRE_TEMPLATE = 'Загрузите фото чек\\-листа\\.\n' + GlobalTxt.SUGGEST_CANCEL_TEXT + '\n\n' \
                                   '*Заказ №*: {}\n' \
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
                                   '*Тип заказа*: {}'
