from http.server import BaseHTTPRequestHandler
from urllib import parse
import logging

from source.BitrixFieldsAliases import *
from source import creds


logger = logging.getLogger(__name__)


class PostHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            logger.info("New POST request accepted!")
            query = parse.urlparse(self.path).query
            query_components = parse.parse_qs(query, keep_blank_values=True)
            logger.info("Accepted query components: %s", query_components)

            if WEBHOOK_SECRET_ALIAS in query_components \
                    and query_components[WEBHOOK_SECRET_ALIAS][0] == creds.BITRIX_WEBHOOK_SECRET:

                action = query_components[WEBHOOK_ACTION_ALIAS][0]

                if action == None:
                    pass

            else:
                logger.error('Wrong Bitrix webhook secret passed or not provided')

        except Exception as e:
            logger.error('HTTP request handling error: %s', e)

