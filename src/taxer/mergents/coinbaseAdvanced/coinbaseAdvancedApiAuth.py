from cryptography.hazmat.primitives import serialization
import jwt
from requests.auth import AuthBase
import time


class CoinbaseAdvancedApiAuth(AuthBase):
    def __init__(self, apiKeyName:str, privateKey:str):
        self.__apiKeyName = apiKeyName
        self.__privateKey = privateKey

    def __call__(self, request):
        request.headers.update(CoinbaseAdvancedApiAuth.__getHeaders(request, self.__apiKeyName, self.__privateKey))
        return request

    @staticmethod
    def __getHeaders(request, apiKeyName, privateKey):
        privateKeyBytes = privateKey.encode('utf-8')
        privateKey = serialization.load_pem_private_key(privateKeyBytes, password=None)
        payload = {
            'sub': apiKeyName,
            'iss': "coinbase-cloud",
            'nbf': int(time.time()),
            'exp': int(time.time()) + 60,
            'aud': ['retail_rest_api_proxy'],
            'uri': f"{request.method} {request.path_url}",
        }
        token = jwt.encode(
            payload,
            privateKey,
            algorithm = 'ES256',
            headers = {'kid': apiKeyName, 'nonce': str(int(time.time()))},
        )
        return {
            'Content-Type': 'Application/JSON',
            'Authorization: Bearer ': token
        }
