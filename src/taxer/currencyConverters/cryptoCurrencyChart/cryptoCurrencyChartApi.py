import json
import logging
import requests

from ..currencyConverterApi import CurrencyConverterApi


class CryptoCurrencyChartApi(CurrencyConverterApi):
    __log = logging.getLogger(__name__)

    def __init__(self, config):
        self.__config = config
        self.__session = requests.Session()

    def __del__(self):
        self.__session.close()

    def getSymbols(self):
        CryptoCurrencyChartApi.__log.info('Get ids')
        query = 'https://{}:{}@{}/coin/list'.format(self.__config['key'], self.__config['secret'], self.__config['url'])
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['coins']

    def getRate(self, symbol, date):
        query = 'https://{}:{}@{}/coin/view/{}/{}/CHF'.format(self.__config['key'], self.__config['secret'], self.__config['url'], symbol, date.strftime('%Y-%m-%d'))
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['coin']['price']
