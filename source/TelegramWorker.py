from .UserStore import UserStore
from .User import User
from . import creds
from .TelegramCommandsHandler import *
import requests
import logging
import time


class TgWorker:
    USERS = UserStore()
    MESSAGE_UPDATE_TYPE = 'message'
    # last update offset / incoming msg limit / long polling timeout / allowed messages types
    GET_UPDATES_PARAMS = {'offset': 0, 'limit': 100, 'timeout': 30, 'allowed_updates': [MESSAGE_UPDATE_TYPE]}
    REQUESTS_TIMEOUT = 1.5 * GET_UPDATES_PARAMS['timeout']
    REQUESTS_MAX_ATTEMPTS = 5
    GLOBAL_LOOP_ERROR_TIMEOUT = 60  # seconds
    SESSION = requests.session()
    CommandsHandler = None

    def __init__(self):
        self.CommandsHandler = TelegramCommandsHandler(self)

    def send_request(self, method, params, custom_error_text=''):

        for a in range(self.REQUESTS_MAX_ATTEMPTS):
            try:
                response = self.SESSION.post(url=creds.TG_API_URL + method, proxies=creds.HTTPS_PROXY,
                                             json=params, timeout=self.REQUESTS_TIMEOUT)

                if response:
                    json = response.json()

                    if json['ok']:
                        return json
                    else:
                        logging.error('TG bad response %s : Attempt: %s, Called: %s : Request params: %s',
                                      a, json, custom_error_text, params)
                else:
                    logging.error('TG response failed%s : Attempt: %s, Called: %s : Request params: %s',
                                  a, response.text, custom_error_text, params)
            except Exception as e:
                logging.error('Sending TG api request %s', e)

        return {}

    def send_file_dl_request(self, url):
        for a in range(self.REQUESTS_MAX_ATTEMPTS):
            try:
                response = requests.get(url, proxies=creds.HTTPS_PROXY, timeout=self.REQUESTS_TIMEOUT)

                if response:
                    return response
                else:
                    logging.error('TG downloading file bad response attempt %s : URL: %s ', a, url)
            except Exception as e:
                logging.error('Downloading TG file %s', e)

        return {}

    def send_message(self, chat_id, message_object, formatting='Markdown'):
        message_object['chat_id'] = chat_id
        message_object['parse_mode'] = formatting
        return self.send_request('sendMessage', message_object, 'Message sending')

    def get_user_file(self, user, file_id):
        file = self.send_request('getFile', {'file_id': file_id})
        file_path = None
        file_extension = None

        try:
            file_path = file['result']['file_path']
        except Exception:
            self.send_message(user.get_chat_id(), {'text': TextSnippets.FILE_LOADING_FAILED + '\n' +
                                                           TextSnippets.SUGGEST_CANCEL_TEXT})
            return None, None

        result = self.send_file_dl_request(creds.FILE_DL_LINK.format(file_path))

        if not result:
            self.send_message(user.get_chat_id(), {'text': TextSnippets.FILE_LOADING_FAILED + '\n' +
                                                           TextSnippets.SUGGEST_CANCEL_TEXT})
            return None, None

        file_extension = file_path.split('.')[-1]

        return result.content, file_extension

    def handle_user_command(self, user, message):
        try:
            self.CommandsHandler.handle_command(message)
        except Exception as e:
            logging.error('Handling command: %s', e)
            user.clear_deal_photos()
            user.clear_checklist()
            user.set_state_menu()
            self.send_message(message['chat']['id'], {'text': TextSnippets.UNKNOWN_ERROR + '\n'
                                                              + TextSnippets.BOT_HELP_TEXT})

    def handle_message(self, message):
        user_id = message['from']['id']
        chat_id = message['chat']['id']

        # has user been already cached?-
        if self.USERS.has_user(user_id):
            user = self.USERS.get_user(user_id)

            if chat_id != user.get_chat_id():
                user._chat_id = chat_id

            if user.has_provided_password():
                self.handle_user_command(user, message)
            else:
                try:
                    provided_password = message['text']

                    if provided_password == creds.GLOBAL_AUTH_PASSWORD:
                        self.USERS.authorize(user_id, provided_password)
                    else:
                        logging.error('Invalid password authorization attempt, user: ' + user_id)
                        raise Exception()
                except Exception:
                    self.send_message(chat_id, {'text': TextSnippets.AUTHORIZATION_UNSUCCESSFUL})
                else:
                    self.send_message(chat_id, {'text': TextSnippets.AUTHORIZATION_SUCCESSFUL})
                    self.send_message(chat_id, {'text': TextSnippets.BOT_HELP_TEXT})

        else:
            self.send_message(chat_id, {'text': TextSnippets.REQUEST_PASS_MESSAGE})
            self.USERS.add_user(user_id, User())

    def handle_update(self, update):
        try:
            if self.MESSAGE_UPDATE_TYPE in update:
                self.handle_message(update[self.MESSAGE_UPDATE_TYPE])
            else:
                raise Exception('Unknown update type: %s' % update)
        except Exception as e:
            logging.error('Handling TG response update: %s', e)

    def base_response_handler(self, json_response):
        try:
            if json_response['result']:
                logging.info(json_response)

            max_update_id = self.GET_UPDATES_PARAMS['offset']
            updates = json_response['result']
            for update in updates:
                cur_update_id = update['update_id']
                if cur_update_id > max_update_id:
                    max_update_id = cur_update_id

                # TODO: thread for each user?
                self.handle_update(update)

            if updates:
                self.GET_UPDATES_PARAMS['offset'] = max_update_id + 1

        except Exception as e:
            logging.error('Base TG response exception handler: %s', e)

    # entry point
    def run(self):
        self.USERS.load_user_store()

        while True:
            response = self.send_request('getUpdates', self.GET_UPDATES_PARAMS, 'Main getting updates')

            # prevent logs spamming in case of network problems
            if not response:
                time.sleep(self.GLOBAL_LOOP_ERROR_TIMEOUT)

            self.base_response_handler(response)
            # TODO: multithreading timer for updates?
            self.USERS.update_user_store()
