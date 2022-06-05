import json
import requests

from ..currencyConverterApi import CurrencyConverterApi


class ExchangeRateHostApi(CurrencyConverterApi):
    def __init__(self, config):
        self.__config = config
        self.__session = requests.Session()

    def __del__(self):
        self.__session.close()

    def getSymbols(self):
        query = '{}/symbols'.format(self.__config['url'])
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['symbols'].keys()

    def getRate(self, symbol, date):
        query = '{}/{}?base={}&symbols={}'.format(self.__config['url'], date.strftime('%Y-%m-%d'), symbol, 'CHF')
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['rates']['CHF']
