import json
import logging
import requests

from ..currencyConverterApi import CurrencyConverterApi


class ExchangeRateHostApi(CurrencyConverterApi):
    __log = logging.getLogger(__name__)

    def __init__(self, config):
        self.__config = config
        self.__session = requests.Session()

    def __del__(self):
        self.__session.close()

    def getSymbols(self):
        ExchangeRateHostApi.__log.info('Get ids')
        query = '{}/symbols'.format(self.__config['url'])
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['symbols'].keys()

    def getRate(self, symbol, date):
        query = '{}/{}?base={}&symbols={}'.format(self.__config['url'], date.strftime('%Y-%m-%d'), symbol, 'CHF')
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['rates']['CHF']
