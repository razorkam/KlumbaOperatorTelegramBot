# all tasks related to orders storage system
# relates to Client Photos Viewer functions
import os
import hashlib
import schedule
from threading import Thread
import time
import random
import logging
import sqlite3
import shutil

random.seed()


class StorageWorker:
    ORDERS_DIR = os.path.join(os.getcwd(), 'orders_data')
    ORDER_DIGEST_LIMIT = 16
    DATABASE_NAME = 'orders.db'
    CONN = sqlite3.connect(os.path.join(ORDERS_DIR, DATABASE_NAME))
    ORDER_EXPIRED_TIME_LIMIT = 24 * 60 * 60  # seconds to order expiration
    LOCKFILE_PATH = os.path.join(ORDERS_DIR, 'file.lock')
    LOCK_TIMEOUT = 60  # sec
    MAINTENANCE_TIME = '03:00'
    SCHEDULING_SLEEP_INTERVAL = 60 * 60  # 1h

    @staticmethod
    def save_order(user, deal_id):
        try:
            photos = user.get_deal_photos()

            order_digest = ''
            for p in photos:
                order_digest += p.name_big

            order_digest += (str(time.time()) + str(random.random()))
            order_digest = hashlib.sha256(order_digest.encode()).hexdigest()[:StorageWorker.ORDER_DIGEST_LIMIT]

            while os.path.isdir(os.path.join(StorageWorker.ORDERS_DIR, order_digest)):
                order_digest += str(random.random())
                order_digest = hashlib.sha256(order_digest.encode()).hexdigest()[:StorageWorker.ORDER_DIGEST_LIMIT]

            order_dir_path = os.path.join(StorageWorker.ORDERS_DIR, order_digest)

            os.mkdir(order_dir_path)

            for p in photos:
                with open(os.path.join(StorageWorker.ORDERS_DIR, *(order_digest, p.name_big)), 'wb') as f:
                    bytes_written = f.write(p.data_big)
                    if bytes_written != len(p.data_big):
                        raise Exception("Error writing binary data of photo: inconsistent write attempt")

            cursor = StorageWorker.CONN.cursor()
            cursor.execute('insert into orders values(?,?)', (order_digest, deal_id))
            StorageWorker.CONN.commit()

        except Exception as e:
            logging.error("Storage worker critical error - order hasn't been handled: %s", e)
            return None

        return order_digest

    @staticmethod
    def init_db():
        cursor = StorageWorker.CONN.cursor()

        cursor.execute('create table if not exists orders (digest text, id text)')
        StorageWorker.CONN.commit()

    @staticmethod
    def maintain_storage():
        StorageWorker.init_db()

        def service_job():
            try:
                logging.info("Running orders dir maintenance now!")
                cur_time = time.time()
                m_conn = sqlite3.connect(os.path.join(StorageWorker.ORDERS_DIR, StorageWorker.DATABASE_NAME))
                cursor = m_conn.cursor()

                for entry in os.scandir(StorageWorker.ORDERS_DIR):
                    delta_time = cur_time - entry.stat().st_mtime

                    order_digest = ''
                    try:
                        if entry.is_dir() and delta_time >= StorageWorker.ORDER_EXPIRED_TIME_LIMIT:  # expired
                            order_digest = entry.name
                            cursor.execute('delete from orders where digest=?', (order_digest,))
                            shutil.rmtree(entry.path)
                    except Exception as e:
                        logging.error("Maintenance entry {} error: {}".format(order_digest, e))

                m_conn.commit()
            except Exception as e:
                logging.error("Maintenance service job error: %s", e)

        schedule.every().day.at(StorageWorker.MAINTENANCE_TIME).do(service_job)

        def thread_fun():
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(StorageWorker.SCHEDULING_SLEEP_INTERVAL)
            except:
                pass

        thread = Thread(target=thread_fun, daemon=True)
        thread.start()

    @staticmethod
    def get_deal_id(digest):
        try:
            conn = sqlite3.connect(os.path.join(StorageWorker.ORDERS_DIR, StorageWorker.DATABASE_NAME))
            cursor = conn.cursor()
            cursor.execute('select * from orders where digest=?', (digest,))
            data = cursor.fetchall()

            if len(data) == 0:
                return None
            else:
                return data[0][1]
        except Exception as e:
            logging.error('Error getting deal id by digest: %s', e)
            return None

    @staticmethod
    def get_deal_photos_path(digest):
        photos_path_list = []

        try:
            for photo_entry in os.scandir(os.path.join(StorageWorker.ORDERS_DIR, digest)):
                photos_path_list.append('/' + digest + '/' + photo_entry.name)

        except Exception as e:
            logging.error('Error traversing deal photos to return: %s', e)
            return []

        return photos_path_list
