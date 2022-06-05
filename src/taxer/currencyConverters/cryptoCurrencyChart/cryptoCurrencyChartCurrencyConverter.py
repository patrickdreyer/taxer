from decimal import Decimal
import logging
import os

from .cryptoCurrencyChartApi import CryptoCurrencyChartApi
from ..csvFileDict import CsvFileDict
from ..currencyConverter import CurrencyConverter


class CryptoCurrencyChartCurrencyConverter(CurrencyConverter):
    __log = logging.getLogger(__name__)

    def __init__(self, config, cachePath):
        self.__config = config
        self.__api = CryptoCurrencyChartApi(self.__config)
        self.__ids = CsvFileDict(os.path.join(cachePath, self.__config['idsFileName']), ['unit', 'id'])
        self.__rates = CsvFileDict(os.path.join(cachePath, self.__config['ratesFileName']), ['key', 'rate'])

    def load(self):
        if not self.__ids.load():
            self.__loadIds()
        self.__rates.load()

    def store(self):
        self.__ids.store()
        self.__rates.store()

    @property
    def id(self):
        return self.__config['id']

    @property
    def symbols(self):
        return self.__ids().keys()

    def exchangeRate(self, symbol, date):
        cacheKey = '{0}{1}'.format(symbol, date.strftime('%Y%m%d'))
        if not cacheKey in self.__rates():
            CryptoCurrencyChartCurrencyConverter.__log.info("Fetch exchange rate; symbol='%s', date='%s'", symbol, date)
            id = self.__ids[symbol]
            self.__rates[cacheKey] = self.__api.getRate(id, date)
        return Decimal(self.__rates[cacheKey])

    def __loadIds(self):
        CryptoCurrencyChartCurrencyConverter.__log.info('Get ids')
        coins = self.__api.getSymbols()
        for coin in coins:
            self.__ids[coin['symbol'].upper()] = coin['id']
