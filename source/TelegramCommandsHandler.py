import logging
import base64

from .BitrixWorker import BitrixWorker
from .StorageWorker import *
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
            # store raw photo data to save it on disk later
            user.add_deal_photo(Photo(unique_id_small + '_S' '.' + file_extension_small,
                                      unique_id_big + '_B' + '.' + file_extension_big,
                                      photo_content_small,
                                      photo_content_big, file_id_big))

            self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.PHOTO_LOADED_TEXT})

            logging.info('Chat id %s uploaded photo %s', user.get_chat_id(), unique_id_small)

    def deal_photos_update(self, user, deal_id):
        digest = StorageWorker.save_order(user, deal_id)

        if not digest:
            self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.UNKNOWN_ERROR})
            return False

        return self.BitrixWorker.update_deal_image(user, deal_id)

    def handle_menu_action(self, user, message):
        chat_id = message['chat']['id']

        if 'text' in message:
            cmd = message['text']

            if cmd == Commands.START or cmd == Commands.CANCEL:
                self.TgWorker.send_message(chat_id, {'text': TextSnippets.BOT_HELP_TEXT})
            elif cmd == Commands.PHOTO_LOAD:
                user.set_state_loading_photos()
                user.clear_deal_photos()
                self.TgWorker.send_message(chat_id, {'text': TextSnippets.ASK_FOR_PHOTO_TEXT})

            elif cmd == Commands.CHECKLIST_LOAD:
                user.set_state_checklist_setting_deal_number()
                user.clear_deal_data()
                self.TgWorker.send_message(chat_id, {'text': TextSnippets.ASK_FOR_DEAL_NUMBER_TEXT})
            elif cmd == Commands.COURIER_SET:
                user.set_state_setting_courier_deal_number()
                self.TgWorker.send_message(chat_id, {'text': TextSnippets.ASK_FOR_DEAL_NUMBER_TEXT})
            else:
                self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND + '\n'
                                                             + TextSnippets.BOT_HELP_TEXT})
        else:
            self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND + '\n'
                                                         + TextSnippets.BOT_HELP_TEXT})

    def handle_photo_action(self, user, message):
        chat_id = message['chat']['id']

        if 'photo' in message:
            self.handle_photo_getting(user, message['photo'])
        elif 'text' in message:
            command = message['text']

            if Utils.is_deal_number(command):
                result = self.deal_photos_update(user, command)
                if result:
                    user.set_state_menu()
                    self.TgWorker.send_message(chat_id, {'text': TextSnippets.BOT_HELP_TEXT})
            else:
                self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND + '\n'
                                                             + TextSnippets.SUGGEST_CANCEL_TEXT})
        else:
            self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND + '\n'

                                                         + TextSnippets.SUGGEST_CANCEL_TEXT})

    def generate_courier_suggestions(self, user, is_checklist_step=True):
        couriers = self.BitrixWorker.get_couriers_list(user)
        user.deal_data.couriers_dict = couriers
        courier_id = user.deal_data.courier_id

        if not courier_id or (not is_checklist_step):
            suggestions = TextSnippets.COURIER_SUGGESTION_TEXT
        else:
            suggestions = TextSnippets.COURIER_EXISTS_TEXT.format(couriers[courier_id],
                                                                  Utils.escape_markdown_special_chars(
                                                                      Commands.SKIP_COURIER_SETTING))

        for ck, cv in couriers.items():
            if courier_id != ck:
                suggestions += TextSnippets.COURIER_TEMPLATE.format(cv,
                                                                    Commands.SET_COURIER_PREFIX +
                                                                    Commands.SET_COURIER_DELIMETER + ck)

        return suggestions

    def handle_checklist_deal_number_setting(self, user, message):
        chat_id = message['chat']['id']

        if 'text' in message:
            command = message['text']

            if Utils.is_deal_number(command):
                result = self.BitrixWorker.process_checklist_deal_info(command, user)

                if not result:
                    return

                user.set_state_checklist_setting_courier()

                # suggest possible couriers
                self.TgWorker.send_message(chat_id, {'text': self.generate_courier_suggestions(user)})

                logging.info('Chat id %s setted deal number %s for checklist', user.get_chat_id(), command)

            else:
                self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND + '\n'
                                                             + TextSnippets.SUGGEST_CANCEL_TEXT})

        else:
            self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND + '\n'
                                                         + TextSnippets.SUGGEST_CANCEL_TEXT})

    def generate_checklist_photo_require_text(self, user):
        return TextSnippets.CHECKLIST_PHOTO_REQUIRE_TEMPLATE.format(user.deal_data.deal_id, user.deal_data.order,
                                                                    user.deal_data.contact, user.deal_data.florist,
                                                                    user.deal_data.order_received_by,
                                                                    user.deal_data.incognito,
                                                                    user.deal_data.order_comment,
                                                                    user.deal_data.delivery_comment,
                                                                    user.deal_data.total_sum,
                                                                    user.deal_data.payment_type,
                                                                    user.deal_data.payment_method,
                                                                    user.deal_data.payment_status,
                                                                    user.deal_data.prepaid, user.deal_data.to_pay)

    def handle_courier_setting(self, user, message, is_checklist_step=True):
        chat_id = message['chat']['id']

        if 'text' in message:
            command = message['text']

            if command == Commands.SKIP_COURIER_SETTING or Utils.is_courier_setting_command(command):
                courier_id = command.split(Commands.SET_COURIER_DELIMETER)[-1]

                if courier_id != Commands.SKIP_COURIER_DATA and courier_id not in user.deal_data.couriers_dict:
                    self.TgWorker.send_message(chat_id, {'text': TextSnippets.COURIER_UNKNOWN_ID_TEXT + '\n'
                                                                 + TextSnippets.SUGGEST_CANCEL_TEXT})
                    return

                user.deal_data.courier_id = courier_id

                if is_checklist_step:
                    self.TgWorker.send_message(chat_id, {'text': self.generate_checklist_photo_require_text(user)})
                    if courier_id != Commands.SKIP_COURIER_DATA:
                        logging.info('Chat id %s set courier %s for checklist', user.get_chat_id(),
                                     user.deal_data.couriers_dict[courier_id])

                    user.set_state_checklist_setting_photo()
                else:
                    self.BitrixWorker.update_deal_courier(user)

            else:
                self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND + '\n'
                                                             + TextSnippets.SUGGEST_CANCEL_TEXT})

        else:
            self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND + '\n'
                                                         + TextSnippets.SUGGEST_CANCEL_TEXT})

    def handle_checklist_photo_setting(self, user, message):
        chat_id = message['chat']['id']

        if 'photo' in message:
            photo = message['photo'][-1]  # small

            file_id = photo['file_id']
            photo_content, file_extension = self.TgWorker.get_user_file(user, file_id)

            encoded_data = None

            if photo_content and file_extension:
                unique_id = photo['file_unique_id']
                encoded_data = base64.b64encode(photo_content).decode('ascii')
                user.deal_data.photo_data = encoded_data
                user.deal_data.photo_name = unique_id + '.' + file_extension

                result = self.BitrixWorker.update_deal_checklist(user)

                if result:
                    user.set_state_menu()
                    self.TgWorker.send_message(chat_id, {'text': TextSnippets.BOT_HELP_TEXT})
                    logging.info('Chat id %s completed checklist step with photo %s', user.get_chat_id(), unique_id)

        else:
            self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND + '\n'
                                                         + TextSnippets.SUGGEST_CANCEL_TEXT})

    def handle_checklist_action(self, user, message):
        if user.is_checklist_deal_number_setting():
            self.handle_checklist_deal_number_setting(user, message)
        elif user.is_checklist_courier_setting():
            self.handle_courier_setting(user, message)
        elif user.is_checklist_photo_setting():
            self.handle_checklist_photo_setting(user, message)
        else:
            logging.error('Unknown checklist state: %s', user.get_state())

    def handle_setting_courier_deal_number(self, user, message):
        chat_id = message['chat']['id']

        if 'text' in message:
            command = message['text']

            if Utils.is_deal_number(command):
                result = self.BitrixWorker.process_checklist_deal_info(command, user, check_approved=False)

                if not result:
                    return

                user.set_state_setting_courier_courier_choose()

                # suggest possible couriers
                courier_suggestions = self.generate_courier_suggestions(user, False)
                courier = None

                if user.deal_data.courier_id in user.deal_data.couriers_dict:
                    courier = user.deal_data.couriers_dict[user.deal_data.courier_id]

                courier = Utils._stringify_field(courier)

                deal_preview = TextSnippets.SETTING_COURIER_DEAL_INFO_TEMPLATE.format(user.deal_data.deal_id,
                                                                                      user.deal_data.order,
                                                                                      user.deal_data.contact,
                                                                                      user.deal_data.florist,
                                                                                      user.deal_data.order_received_by,
                                                                                      user.deal_data.incognito,
                                                                                      user.deal_data.order_comment,
                                                                                      user.deal_data.delivery_comment,
                                                                                      user.deal_data.total_sum,
                                                                                      user.deal_data.payment_type,
                                                                                      user.deal_data.payment_method,
                                                                                      user.deal_data.payment_status,
                                                                                      user.deal_data.prepaid,
                                                                                      user.deal_data.to_pay, courier)

                self.TgWorker.send_message(chat_id, {'text': deal_preview})
                self.TgWorker.send_message(chat_id, {'text': courier_suggestions})

                logging.info('Chat id %s set deal number %s for setting courier', user.get_chat_id(), command)

            else:
                self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND + '\n'
                                                             + TextSnippets.SUGGEST_CANCEL_TEXT})

        else:
            self.TgWorker.send_message(chat_id, {'text': TextSnippets.UNKNOWN_COMMAND + '\n'
                                                         + TextSnippets.SUGGEST_CANCEL_TEXT})

    def handle_setting_courier_courier_choose(self, user, message):
        self.handle_courier_setting(user, message, False)
        user.reset_state()
        self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.BOT_HELP_TEXT})

    def handle_setting_courier_action(self, user, message):
        if user.is_setting_courier_deal_number_setting():
            self.handle_setting_courier_deal_number(user, message)
        elif user.is_setting_courier_courier_choose():
            self.handle_setting_courier_courier_choose(user, message)
        else:
            logging.error('Unknown setting courier state: %s', user.get_state())

    def handle_command(self, message):
        user_id = message['from']['id']
        chat_id = message['chat']['id']
        user = self.TgWorker.USERS.get_user(user_id)

        if 'text' in message and (message['text'] == Commands.CANCEL or message['text'] == Commands.START):
            user.reset_state()
            self.TgWorker.send_message(chat_id, {'text': TextSnippets.BOT_HELP_TEXT})
            return

        if user.is_in_menu():
            self.handle_menu_action(user, message)
        elif user.is_photos_loading():
            self.handle_photo_action(user, message)
        elif user.is_checklist_actions_handling():
            self.handle_checklist_action(user, message)
        elif user.is_setting_courier_actions_handling():
            self.handle_setting_courier_action(user, message)
        else:
            logging.error('Unknown user state: %s', user.get_state())
