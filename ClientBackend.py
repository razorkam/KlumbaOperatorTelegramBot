from flask import Flask, request, jsonify, Response
from source.StorageWorker import *
from source.BitrixWorker import *

import logging
from logging.handlers import RotatingFileHandler

LOG_MAX_SIZE = 2 * 1024 * 1024  # 2 mbytes

app = Flask(__name__)
bw = BitrixWorker(None)

APP_PORT = 8083

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
log_handler = RotatingFileHandler('client_backend.log', mode='a', maxBytes=LOG_MAX_SIZE,
                                  backupCount=5)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(handlers=[log_handler])


@app.route('/')
def hello():
    return 'Hello!'


@app.route('/<string:digest>', methods=['GET'])
def get_deal_info(digest):
    try:
        logging.info('New get deal info request: %s', digest)

        deal_id = StorageWorker.get_deal_id(digest)

        if not deal_id:
            return Response('Заказ не найден', status=404)

        deal_desc = bw.get_deal_info_for_client(deal_id)

        if deal_desc is False:
            return Response("Ошибка при получении данных заказа", status=503)

        if deal_desc is None:
            return Response('Заказ уже был согласован', status=501)

        deal_desc.photos = StorageWorker.get_deal_photos_path(digest)
        rsp = deal_desc.get_dict()
        rsp['id'] = deal_id

        return jsonify(rsp)
    except Exception as e:
        logging.error('Get deal request error: %s', e)
        return Response('Внутренняя ошибка сервера', status=500)


@app.route('/<string:digest>', methods=['POST'])
def update_deal(digest):
    try:
        logging.info('New update deal info request: %s', digest)

        deal_id = StorageWorker.get_deal_id(digest)

        if not deal_id:
            return Response('Заказ не найден', status=404)

        stage_check_result = bw.check_deal_stage_before_update(deal_id)

        if stage_check_result is None:
            return Response('Внутренняя ошибка при обновлении заказа', status=503)

        if not stage_check_result:
            return Response('Заказ уже был согласован', status=501)

        data = None
        if request.is_json:
            data = request.json
            pass
        else:
            return Response('Данные клиента должны быть переданы в виде json', status=400)

        logging.info('Request body json data: %s', data)

        result = bw.update_deal_by_client(deal_id, data)

        if not result:
            return Response('Внутренняя ошибка при обновлении заказа', status=503)

        return Response('Заказ успешно обновлен!', status=200)

    except Exception as e:
        logging.error('Update deal request error: %s', e)
        return Response('Внутренняя ошибка сервера', status=500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT)
