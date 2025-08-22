from cryptography.hazmat.primitives import serialization
import jwt
from requests.auth import AuthBase
import time
import secrets
from urllib.parse import urlparse


class CoinbaseApiAuth(AuthBase):
    def __init__(self, keyName:str, keySecret:str):
        self.__keyName = keyName
        self.__keySecret = keySecret

    def __call__(self, request):
        request.headers.update(CoinbaseApiAuth.__getHeaders(request, self.__keyName, self.__keySecret))
        return request

    @staticmethod
    def __getHeaders(request, keyName, keySecret):
        keySecretBytes = keySecret.encode('utf-8')
        keySecret = serialization.load_pem_private_key(keySecretBytes, password=None)
        urlParts = urlparse(request.url)
        payload = {
            'sub': keyName,
            'iss': "cdp",
            'nbf': int(time.time()),
            'exp': int(time.time()) + 120,
            'uri': f"{request.method} {urlParts.netloc}{urlParts.path}",
        }
        token = jwt.encode(
            payload,
            keySecret,
            algorithm = 'ES256',
            headers = {'kid': keyName, 'nonce': secrets.token_hex()},
        )
        return {
            'Content-Type': 'Application/JSON',
            'Authorization': 'Bearer {}'.format(token)
        }
