import collections
import datetime
import json
import logging
import requests
import time
from urllib.parse import urlparse

from ..currencyConverterApi import CurrencyConverterApi


class CryptoCurrencyChartApi(CurrencyConverterApi):
    __log = logging.getLogger(__name__)
    __callUnit = datetime.timedelta(seconds=1)
    __callsPerUnit = 10
    __calls = collections.deque(maxlen=__callsPerUnit)

    def __init__(self, config):
        self.__config = config
        parts = urlparse(self.__config['url'])
        self.__config['url'] = '{}://{}:{}@{}{}'.format(parts.scheme, self.__config['key'], self.__config['secret'], parts.netloc, parts.path)
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
        self.__throttle()
        query = '{}{}'.format(self.__config['url'], query)
        response = self.__session.get(query)
        return json.loads(response.content)

    def __throttle(self):
        self.__calls.append(datetime.datetime.now())
        size = len(self.__calls)
        if size < self.__calls.maxlen:
            return
        newest = self.__calls[0]
        oldest = self.__calls[size-1]
        difference = newest - oldest
        if difference > CryptoCurrencyChartApi.__callUnit:
            return
        wait = (CryptoCurrencyChartApi.__callUnit - difference).microseconds / 1000000
        time.sleep(wait)