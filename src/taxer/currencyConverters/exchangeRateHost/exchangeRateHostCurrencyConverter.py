from decimal import Decimal
import logging
import os

from .exchangeRateHostApi import ExchangeRateHostApi
from ..csvFileDict import CsvFileDict
from ..currencyConverter import CurrencyConverter
from ..dummySymbolMapper import DummySymbolMapper


class ExchangeRateHostCurrencyConverter(CurrencyConverter):
    __log = logging.getLogger(__name__)

    def __init__(self, config, cachePath):
        self.__config = config
        self.__api = ExchangeRateHostApi(self.__config)
        self.__ids = DummySymbolMapper(self.__api)
        self.__rates = CsvFileDict(os.path.join(cachePath, self.__config['fileName']), ['key', 'rate'])

    def load(self):
        self.__ids.load()
        self.__rates.load()

    def store(self):
        self.__ids.store()
        self.__rates.store()

    @property
    def id(self):
        return self.__config['id']

    @property
    def symbols(self):
        return self.__ids.symbols

    def exchangeRate(self, symbol, date):
        cacheKey = '{0}{1}'.format(symbol, date.strftime('%Y%m%d'))
        if not cacheKey in self.__rates():
            ExchangeRateHostCurrencyConverter.__log.info("Fetch exchange rate; symbol='%s', date='%s'", symbol, date)
            id = self.__ids.map(symbol)
            self.__rates[cacheKey] = self.__api.getRate(id, date)
        return Decimal(self.__rates[cacheKey])
