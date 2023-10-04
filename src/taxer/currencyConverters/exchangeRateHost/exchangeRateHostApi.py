import json
import logging
import requests

from ..currencyConverterApi import CurrencyConverterApi


class ExchangeRateHostApi(CurrencyConverterApi):
    __log = logging.getLogger(__name__)

    def __init__(self, url:str, key:str):
        self.__url = url
        self.__key = key
        self.__session = requests.Session()

    def __del__(self):
        self.__session.close()

    def getSymbols(self):
        ExchangeRateHostApi.__log.info('Get ids')
        content = self.__get('/symbols')
        return content['symbols'].keys()

    def getRate(self, symbol, date):
        content = self.__get('/convert?access_key={}&date={}&from={}&to={}&amount={}'.format(self.__key, date.strftime('%Y-%m-%d'), symbol, 'CHF', 1))
        return content['result']

    def __get(self, query):
        query = '{}{}'.format(self.__url, query)
        response = self.__session.get(query)
        return json.loads(response.content)
