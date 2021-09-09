import os
import schedule
from threading import Thread, Lock, local
import time
import random
import logging
import sqlite3
import pandas as pd

import source.BitrixFieldsAliases as BitrixFieldsAliases
from source.cmd_handlers.PhotosLoading1 import StorageHandlers as Photos1
import source.BitrixWorker as BW
import source.config as cfg

random.seed()

SCHEDULING_SLEEP_INTERVAL = 60  # 1 min
BITRIX_USERS = pd.DataFrame()
BITRIX_USERS_LOCK = Lock()

logger = logging.getLogger(__name__)
BITRIX_DICTS_DB = local()


# general purpose databases
def init_bitrix_dicts_db():
    if not hasattr(BITRIX_DICTS_DB, 'conn'):
        BITRIX_DICTS_DB.conn = sqlite3.connect(os.path.join(cfg.DATA_DIR_NAME, cfg.BITRIX_DICTS_DATABASE))

    cursor = BITRIX_DICTS_DB.conn.cursor()

    cursor.execute('create table if not exists deal_times (id text, val text)')
    BITRIX_DICTS_DB.conn.commit()


def download_bitrix_creds():
    url = BW.get_file_dl_url(BitrixFieldsAliases.BITRIX_USERS_CREDS_FILE_ID)
    # get file from disk -> DOWNLOAD_URL -> pass to Pandas parser with proper engine

    if not url:
        return

    creds_sheet = pd.read_excel(io=url, header=0, engine='openpyxl')

    global BITRIX_USERS
    with BITRIX_USERS_LOCK:
        BITRIX_USERS = creds_sheet


def check_authorization(user):
    if user.bitrix_login and user.bitrix_password:
        with BITRIX_USERS_LOCK:
            id_col_name = BITRIX_USERS.columns[1]
            login_col_name = BITRIX_USERS.columns[2]
            password_col_name = BITRIX_USERS.columns[4]

            row = BITRIX_USERS.loc[(BITRIX_USERS[login_col_name].str.lower() == str(user.bitrix_login).lower()) &
                                   (BITRIX_USERS[password_col_name] == user.bitrix_password)]

            if not row.empty:
                user.bitrix_user_id = int(row[id_col_name].iloc(0)[0])  # authorized user ID
                return True
            else:
                logger.error('Failed authorization attempt, login: %s, password: %s'
                             % (user.bitrix_login, user.bitrix_password))
                user.bitrix_user_id = None
                return False


def load_bitrix_dicts():
    BW.load_dicts()

    # separate thread connection
    if not hasattr(BITRIX_DICTS_DB, 'conn'):
        BITRIX_DICTS_DB.conn = sqlite3.connect(os.path.join(cfg.DATA_DIR_NAME, cfg.BITRIX_DICTS_DATABASE))

    cursor = BITRIX_DICTS_DB.conn.cursor()

    # some dicts need to be saved to use in Client backend process
    cursor.execute('delete from deal_times')
    cursor.executemany('insert into deal_times values (?,?)', BW.DEAL_TIMES.items())
    BITRIX_DICTS_DB.conn.commit()


def maintain_storage():
    init_bitrix_dicts_db()
    Photos1.init_db()
    download_bitrix_creds()
    load_bitrix_dicts()

    schedule.every().day.at(Photos1.ORDERS_CLEANUP_TIME).do(Photos1.orders_cleanup_job)
    schedule.every(10).minutes.do(download_bitrix_creds)
    schedule.every(10).minutes.do(load_bitrix_dicts)

    def thread_fun():
        while True:
            try:
                schedule.run_pending()
                time.sleep(SCHEDULING_SLEEP_INTERVAL)
            except Exception as e:
                logger.error("Scheduler thread error: %s", e)

    thread = Thread(target=thread_fun, daemon=True)
    thread.start()
