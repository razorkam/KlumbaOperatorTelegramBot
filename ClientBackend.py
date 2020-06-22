from flask import Flask, request, jsonify, Response
from source.StorageWorker import *
from source.BitrixWorker import *

app = Flask(__name__)
bw = BitrixWorker(None)


@app.route('/')
def hello():
    return 'Hello!'


@app.route('/<string:digest>', methods=['GET'])
def get_deal_info(digest):
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


@app.route('/<string:digest>', methods=['POST'])
def update_deal(digest):
    deal_id = StorageWorker.get_deal_id(digest)

    if not deal_id:
        return Response('Order not found', status=404)

