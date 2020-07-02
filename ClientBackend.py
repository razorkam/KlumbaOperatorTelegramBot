from flask import Flask, request, jsonify, Response
from source.StorageWorker import *
from source.BitrixWorker import *

import logging
from logging.handlers import RotatingFileHandler

LOG_MAX_SIZE = 2 * 1024 * 1024 # 2 mbytes

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
        deal_id = StorageWorker.get_deal_id(digest)

        if not deal_id:
            return Response('Order not found', status=404)

        deal_desc = bw.get_deal_info_for_client(deal_id)

        if not deal_desc:
            return Response("Can't get deal data", status=503)

        deal_desc.photos = StorageWorker.get_deal_photos_path(digest)
        rsp = deal_desc.get_dict()
        rsp['id'] = deal_id

        return jsonify(rsp)
    except Exception as e:
        logging.error('Get deal request error: %s', e)
        return Response('Internal server error', status=500)


@app.route('/<string:digest>', methods=['POST'])
def update_deal(digest):
    try:
        deal_id = StorageWorker.get_deal_id(digest)

        if not deal_id:
            return Response('Order not found', status=404)

        data = None
        if request.is_json:
            data = request.json
            pass
        else:
            return Response('Request should be in json form', status=400)

        result = bw.update_deal_by_client(deal_id, data)

        if not result:
            return Response('Error updating deal', status=500)

    except Exception as e:
        logging.error('Update deal request error: %s', e)
        return Response('Internal server error', status=500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT)
