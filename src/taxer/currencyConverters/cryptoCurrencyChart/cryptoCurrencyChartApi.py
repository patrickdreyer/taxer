import json
import requests

from ..currencyConverterApi import CurrencyConverterApi


class CryptoCurrencyChartApi(CurrencyConverterApi):
    def __init__(self, config):
        self.__config = config
        self.__session = requests.Session()

    def __del__(self):
        self.__session.close()

    def getSymbols(self):
        query = 'https://{}:{}@{}/coin/list'.format(self.__config['apiKey'], self.__config['apiSecret'], self.__config['apiUrl'])
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['coins']

    def getRate(self, symbol, date):
        query = 'https://{}:{}@{}/coin/view/{}/{}/CHF'.format(self.__config['apiKey'], self.__config['apiSecret'], self.__config['apiUrl'], symbol, date.strftime('%Y-%m-%d'))
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['coin']['price']
