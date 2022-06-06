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
        query = '{}/coins/list'.format(self.__config['url'])
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content

    def getRate(self, symbol, date):
        query = '{}/coins/{}/history?date={}&localization=false'.format(self.__config['url'], symbol, date.strftime('%d-%m-%Y'))
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['market_data']['current_price']['chf']
