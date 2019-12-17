import pickle
import logging


class UserStore:
    USER_STORE_NAME = 'users.pickle'
    _user_store = {} #{ user_id : User }
    _is_synchronized = False

    def has_user(self, user_id):
        return user_id in self._user_store

    def get_user(self, user_id):
        return self._user_store[user_id]

    def load_user_store(self):
        try:
            with open(self.USER_STORE_NAME, 'rb') as store:
                self._user_store = pickle.load(store)
        except Exception as e:
            logging.error('Loading user store %s', e)

    def _save_user_store(self):
        try:
            with open(self.USER_STORE_NAME, 'wb') as store:
                pickle.dump(self._user_store, store)
        except Exception as e:
            logging.error('Saving user store %s', e)

    def update_user_store(self):
        if not self._is_synchronized:
            self._save_user_store()
            self._is_synchronized = True

    def add_user(self, id, user):
        self._user_store[id] = user
        self._is_synchronized = False

    def authorize(self, id, phone_number):
        try:
            user = self._user_store[id]
            user.authorize(phone_number)
            self._is_synchronized = False
        except Exception as e:
            logging.error('Authorizing user %s', e)