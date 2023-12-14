from decimal import Decimal
import logging
import os

from ..container import container
from .csvFileDict import CsvFileDict


class CurrencyConverter:
    def __init__(self, config, api, symbolMapper):
        self.__log = logging.getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))
        self.__id = config['id']
        self.__api = api
        self.__ids = symbolMapper(self.__log, os.path.join(container['config']['cache'], config['idsFileName']), api)
        self.__rates = CsvFileDict(self.__log, os.path.join(container['config']['cache'], config['ratesFileName']), ['key', 'rate'])

    def load(self):
        self.__ids.load()
        self.__rates.load()

    def store(self):
        self.__ids.store()
        self.__rates.store()

    @property
    def id(self):
        return self.__id

    @property
    def symbols(self):
        return self.__ids.symbols

    def exchangeRate(self, symbol, date):
        cacheKey = '{0}{1}'.format(symbol, date.strftime('%Y%m%d'))
        if not cacheKey in self.__rates():
            self.__log.info("Fetch exchange rate; symbol='%s', date='%s'", symbol, date)
            id = self.__ids.map(symbol)
            self.__rates[cacheKey] = self.__api.getRate(id, date)
        return Decimal(self.__rates[cacheKey])
