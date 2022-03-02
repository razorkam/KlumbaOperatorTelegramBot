import source.http_server.TextSnippets as HttpTxt
import source.Commands as Cmd

REQUEST_DECLINE_COMMENT = 'Отклоняем заказ {}\\.\n' \
                          'Напишите, почему?'

REAPPROVE_BUTTON_TEXT = 'Исправлено, отправить на пересогласование \U00002705'
REAPPROVE_BUTTON_KEY_PREFIX = 'festive_reapprove'


FESTIVE_ACTION_PATTERN = '^(' + HttpTxt.FESTIVE_APPROVE_BUTTON_KEY + '|' + HttpTxt.FESTIVE_DECLINE_BUTTON_KEY + ')' \
                         + Cmd.CMD_DELIMETER + r'(\d+)$'
FESTIVE_REAPPROVE_PATTERN = '^' + REAPPROVE_BUTTON_KEY_PREFIX + Cmd.CMD_DELIMETER + r'(\d+)$'


DECLINED_HEADER = '{} *ОТКЛОНЕН*\U0000274C \n'
APPROVED_HEADER = '{} *СОГЛАСОВАН*\U00002705 \n'
REAPPROVED_HEADER = '{} *ИСПРАВЛЕН*\U00002705 \n'


DEAL_DECLINED = '*Ссылка:* {}\n' \
                '*Что заказано:* {}\n' \
                '*Кто отклонил:* {}\n' \
                '*Комментарий по отклонению:* {}'


UNAPPROVED_HEADER_REPLACEMENT_PATTERN = ''