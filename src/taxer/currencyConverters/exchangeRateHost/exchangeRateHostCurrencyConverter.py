from decimal import Decimal
import logging
import os

from .exchangeRateHostApi import ExchangeRateHostApi
from ..csvFileDict import CsvFileDict
from ..currencyConverter import CurrencyConverter


class ExchangeRateHostCurrencyConverter(CurrencyConverter):
    __log = logging.getLogger(__name__)

    def __init__(self, config, cachePath):
        self.__config = config
        self.__api = ExchangeRateHostApi(self.__config)
        self.__rates = CsvFileDict(os.path.join(cachePath, self.__config['fileName']), ['key', 'rate'])

    def load(self):
        self.__symbols = self.__api.getSymbols()
        self.__rates.load()

    def store(self):
        self.__rates.store()

    @property
    def id(self):
        return self.__config['id']

    @property
    def symbols(self):
        return self.__symbols

    def exchangeRate(self, symbol, date):
        cacheKey = '{0}{1}'.format(symbol, date.strftime('%Y%m%d'))
        if not cacheKey in self.__rates():
            ExchangeRateHostCurrencyConverter.__log.info("Fetch exchange rate; symbol='%s', date='%s'", symbol, date)
            self.__rates[cacheKey] = self.__api.getRate(symbol, date)
        return Decimal(self.__rates[cacheKey])
