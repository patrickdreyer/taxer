import json
import logging
import requests

from ..currencyConverterApi import CurrencyConverterApi


class CoinGeckoApi(CurrencyConverterApi):
    __log = logging.getLogger(__name__)

    def __init__(self, config):
        self.__config = config
        self.__session = requests.Session()

    def __del__(self):
        self.__session.close()

    def getSymbols(self):
        CoinGeckoApi.__log.info('Get ids')
        content = self.__get('/coins/list')
        return content

    def getRate(self, symbol, date):
        content = self.__get('/coins/{}/history?date={}&localization=false'.format(symbol, date.strftime('%d-%m-%Y')))
        return content['market_data']['current_price']['chf']

    def __get(self, query):
        query = '{}{}'.format(self.__config['url'], query)
        response = self.__session.get(query)
        return json.loads(response.content)
