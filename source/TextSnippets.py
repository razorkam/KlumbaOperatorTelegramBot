import source.Commands as Commands

FIELD_IS_EMPTY_PLACEHOLDER = 'нет'

REQUEST_LOGIN_MESSAGE = 'Добро пожаловать в *интерфейс оператора Клумба*\\!\n' \
                        'Введите логин:'

REQUEST_PASSWORD_MESSAGE = 'Введите пароль:'

AUTHORIZATION_SUCCESSFUL = 'Авторизация пройдена\\!\n' \
                           'Теперь вы можете использовать возможности бота\\.'

AUTHORIZATION_FAILED = 'Авторизация не пройдена\\. Попробуйте снова\\.\n' \
                             'Введите логин:'

SUGGEST_CANCEL_TEXT = '/{} для возврата в меню\\.'.format(Commands.CANCEL)

ASK_FOR_DEAL_NUMBER_TEXT = 'Введите номер заказа\\.' + '\n' + SUGGEST_CANCEL_TEXT

UNKNOWN_COMMAND = 'Неизвестная команда\\. Попробуйте снова\\.\n' + SUGGEST_CANCEL_TEXT

MENU_TEXT = "Меню: \n" \
            "1\\. Загрузка фото букета и перевод в стадию *Заказ укомплектован*: \n /{} \n\n" \
            "2\\. Загрузка фото чек\\-листа, назначение курьера и перевод в стадию *В доставке*: \n /{}\n\n" \
            "3\\. Назначение курьера на любой стадии заказа \n /{}\n\n" \
            "4\\. Назначение флориста и перевод в стадию *У флориста* \n /{}\n\n" \
            "5\\. Список заказов флориста в стадии *У флориста* \n /{}"

ERROR_BITRIX_REQUEST = 'Произошла ошибка при обращении к серверу\\.\n' \
                       'Попробуйте снова или подождите некоторое время\\.\n' + SUGGEST_CANCEL_TEXT

BITRIX_DEAL_NUMBER_PATTERN = r'^\d+$'

UNKNOWN_ERROR = 'Произошла непредвиденная ошибка\\.\n' \
                'Попробуйте снова, или подождите некоторое время\\.\n' + SUGGEST_CANCEL_TEXT

DEAL_UPDATED = 'Заказ успешно обновлен\\!'

NO_SUCH_DEAL = 'Заказ №{} не существует\\. Попробуйте снова\\.\n' + SUGGEST_CANCEL_TEXT

