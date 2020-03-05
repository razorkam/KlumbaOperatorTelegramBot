import requests
from . import creds
import logging

from .BitrixFieldsAliases import *
from . import TextSnippets


class BitrixWorker:
    SESSION = requests.session()
    REQUESTS_TIMEOUT = 10
    REQUESTS_MAX_ATTEMPTS = 3

    TgWorker = None

    def __init__(self, TGWorker):
        self.TgWorker = TGWorker

    def _send_request(self, user, method, params=None, custom_error_text='', notify_user=True):
        if params is None:
            params = {}

        for a in range(self.REQUESTS_MAX_ATTEMPTS):
            try:
                response = self.SESSION.post(url=creds.BITRIX_API_URL + method,
                                             json=params, timeout=self.REQUESTS_TIMEOUT)

                if response and response.ok:
                    json = response.json()

                    if 'result' in json:
                        return json
                    else:
                        error = 'Bitrix bad response %s : Attempt: %s, Called: %s : Request params: %s' \
                                % (a, json, custom_error_text, params)
                        logging.error(error)
                else:
                    error = 'Bitrix response failed - %s : Attempt: %s,  Called: %s : Request params: %s' \
                            % (a, response.text, custom_error_text, params)
                    logging.error(error)

            except Exception as e:
                error = 'Sending Bitrix api request %s' % e
                logging.error(error)

        if notify_user:
            self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.ERROR_BITRIX_REQUEST})

        return None

    def update_deal_image(self, user, deal_id):
        photos_list = user.get_deal_photos()

        if not photos_list:
            self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.NO_PHOTOS_TEXT})
            return

        deal = self._send_request(user, 'crm.deal.get', {'id': deal_id}, notify_user=False)

        if not deal:
            self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.NO_SUCH_DEAL.format(deal_id)})
            return

        photos_obj = {'id': deal_id, 'fields': {DEAL_SMALL_PHOTO_ALIAS: [], DEAL_BIG_PHOTO_ALIAS: []}}

        for photo in photos_list:
            photos_obj['fields'][DEAL_SMALL_PHOTO_ALIAS].append({'fileData': [photo.name_small,
                                                                              photo.encoded_data_small]})

            photos_obj['fields'][DEAL_BIG_PHOTO_ALIAS].append({'fileData': [photo.name_big,
                                                                            photo.encoded_data_big]})

            logging.info('Chat id %s updating deal %s with photo ids %s:', user.get_chat_id(),
                         deal_id, photo.name_small)

        result = self._send_request(user, 'crm.deal.update', photos_obj)

        if result['result']:
            self.TgWorker.send_message(user.get_chat_id(), {'text': TextSnippets.DEAL_UPDATED_TEXT})

        user.clear_deal_photos()
