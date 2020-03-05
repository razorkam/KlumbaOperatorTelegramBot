import base64
import logging

from .BitrixWorker import BitrixWorker
from . import Utils, Commands
from . import TextSnippets
from .Photo import Photo


class TelegramCommandsHandler:
    TgWorker = None
    BitrixWorker = None

    def __init__(self, TelegramWorker):
        self.TgWorker = TelegramWorker
        self.BitrixWorker = BitrixWorker(TelegramWorker)

    def handle_photo_getting(self, user, photo):
        photo_big = photo[-1]
        photo_small = photo[0]

        file_id_big = photo_big['file_id']
        photo_content_big, file_extension_big = self.TgWorker.get_user_file(user, file_id_big)
        unique_id_big = photo_big['file_unique_id']

        file_id_small = photo_small['file_id']
        photo_content_small, file_extension_small = self.TgWorker.get_user_file(user, file_id_small)
        unique_id_small = photo_small['file_unique_id']

        if photo_content_big and photo_content_small:
            encoded_data_big = base64.b64encode(photo_content_big).decode('ascii')
            encoded_data_small = base64.b64encode(photo_content_small).decode('ascii')

            user.add_deal_photo(Photo(unique_id_small + '.' + file_extension_small,
                                      unique_id_big + '.' + file_extension_big, encoded_data_small, encoded_data_big))

            self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.PHOTO_LOADED_TEXT})

            logging.info('Chat id %s uploaded photo %s', user.get_chat_id(), unique_id_small)

    def handle_deal_update(self, user, deal_id):
        self.BitrixWorker.update_deal_image(user, deal_id)

    def handle_photo_getting_cancel(self, user):
        user.clear_deal_photos()
        self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.PHOTOS_GETTING_CANCELLED})

    def handle_command(self, message):
        user_id = message['from']['id']
        chat_id = message['chat']['id']
        user = self.TgWorker.USERS.get_user(user_id)

        if 'photo' in message:
            self.handle_photo_getting(user, message['photo'])
        elif 'text' in message:
            command = message['text']

            if Utils.is_deal_number(command):
                self.handle_deal_update(user, command)
            elif command == Commands.CANCEL_PHOTO_LOADING:
                self.handle_photo_getting_cancel(user)
            elif command == Commands.START:
                self.TgWorker.send_message(chat_id, {'text': TextSnippets.BOT_HELP_TEXT})
            else:
                self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND})
        else:
            self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND_TYPE})

