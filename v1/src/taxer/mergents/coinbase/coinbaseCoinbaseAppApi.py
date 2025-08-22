import json
import requests

from ...throttler import Throttler
from .coinbaseApiAuth import CoinbaseApiAuth


# https://docs.cdp.coinbase.com/coinbase-app/docs/welcome
class CoinbaseCoinbaseAppApi:
    __pageLimit = 100
    __throttler = Throttler((int)(10000 / 60 / 60))

    def __init__(self, url:str, symbols:list[str], auth:CoinbaseApiAuth):
        self.__url = url
        self.__symbols = symbols
        self.__auth = auth
        self.__session = requests.Session()

    def __del__(self):
        self.__session.close()

    def getTransfers(self):
        accounts = self.__getItems('/v2/accounts', {})['data']
        for accountId in [account['id'] for account in accounts if account['balance']['currency'] in self.__symbols]:
            yield from self.__getPaginated(f"/v2/accounts/{accountId}/transactions", {})
            yield from self.__getPaginated(f"/v2/accounts/{accountId}/deposits", {})
            yield from self.__getPaginated(f"/v2/accounts/{accountId}/withdrawals", {})

    def __getItems(self, path, params):
        response = self.__get(path, params)
        return json.loads(response.content)

    def __getPaginated(self, path, params):
        params['limit'] = CoinbaseCoinbaseAppApi.__pageLimit
        while True:
            response = self.__get(path, params)
            items = json.loads(response.content)['data']
            for item in items:
                params['starting_after'] = item['id']
                yield item
            if not response.headers.get('next_uri'):
                break

    def __get(self, path, params):
        self.__throttler.throttle()
        url = f"{self.__url}{path}"
        response = self.__session.get(url, params = params, auth = self.__auth)
        if (response.status_code != 200):
            raise Exception(f"{response.reason}: {response.text}")
        return response
