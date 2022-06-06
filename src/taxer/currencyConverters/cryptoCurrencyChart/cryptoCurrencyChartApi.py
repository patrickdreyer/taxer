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
        content = self.__get('/coin/list')
        return content['coins']

    def getRate(self, symbol, date):
        content = self.__get('/coin/view/{}/{}/CHF'.format(symbol, date.strftime('%Y-%m-%d')))
        return content['coin']['price']

    def __get(self, query):
        query = 'https://{}:{}@{}{}'.format(self.__config['key'], self.__config['secret'], self.__config['url'], query)
        response = self.__session.get(query)
        return json.loads(response.content)
