import base64
import hashlib
import hmac
from requests.auth import AuthBase
import time


class CoinbaseProApiAuth(AuthBase):
    def __init__(self, config):
        self.__config = config

    def __call__(self, request):
        timestamp = str(time.time())
        message = ''.join([timestamp, request.method, request.path_url, (request.body or '')])
        request.headers.update(CoinbaseProApiAuth.__getHeaders(timestamp, message, self.__config['key'], self.__config['secret'], self.__config['passphrase']))
        return request

    @staticmethod
    def __getHeaders(timestamp, message, api_key, secret_key, passphrase):
        message = message.encode('ascii')
        hmac_key = base64.b64decode(secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
        return {
            'Content-Type': 'Application/JSON',
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': api_key,
            'CB-ACCESS-PASSPHRASE': passphrase
        }
