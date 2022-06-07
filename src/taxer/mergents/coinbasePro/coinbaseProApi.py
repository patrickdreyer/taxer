import json
import requests

from ...throttler import Throttler


class CoinbaseProApi:
    __limit = 1000
    __throttler = Throttler(10)

    def __init__(self, config, auth):
        self.__config = config
        self.__auth = auth
        self.__session = requests.Session()

    def __del__(self):
        self.__session.close()

    def getAllAccounts(self):
        accounts = self.__getItems('/accounts', {})
        return accounts

    def getAllTransfers(self, profileId):
        yield from self.__getPaginated('/transfers', {'profile_id': profileId})

    def getAllFills(self, profileId):
        products = self.__getItems('/products', {})
        productIds = [p['id'] for p in products if p['base_currency'] in self.__config['symbols'] and p['quote_currency'] in self.__config['symbols']]
        for productId in productIds:
            yield from self.__getPaginated('/fills', {'profile_id': profileId, 'product_id': productId})

    def __getItems(self, path, params):
        response = self.__get(path, params)
        return json.loads(response.content)

    def __getPaginated(self, path, params):
        params['limit'] = CoinbaseProApi.__limit
        response = self.__get(path, params)
        items = json.loads(response.content)
        for item in items:
            yield item
        while response.headers.get('CB-AFTER'):
            params['after'] = response.headers['CB-AFTER']
            response = self.__get(path, params)
            for item in json.loads(response.content):
                yield item

    def __get(self, path, params):
        self.__throttler.throttle()
        url = '{}{}'.format(self.__config['url'], path)
        response = self.__session.get(url, params = params, auth = self.__auth)
        if (response.status_code != 200):
            raise Exception('{}: {}'.format(response.reason, json.loads(response.text)['message']))
        return response
