from decimal import Decimal
import logging
import os

from .coinGeckoApi import CoinGeckoApi
from ..csvFileDict import CsvFileDict
from ..currencyConverter import CurrencyConverter


class CoinGeckoCurrencyConverter(CurrencyConverter):
    __log = logging.getLogger(__name__)

    def __init__(self, config, cachePath):
        self.__config = config
        self.__api = CoinGeckoApi(self.__config)
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

    def exchangeRate(self, unit, date):
        cacheKey = '{0}{1}'.format(unit, date.strftime('%Y%m%d'))
        if not cacheKey in self.__rates():
            self.__fetchExchangeRate(unit, date, cacheKey)
        return Decimal(self.__rates[cacheKey])

    def __fetchExchangeRate(self, unit, date, cacheKey):
        CoinGeckoCurrencyConverter.__log.info("Fetch exchange rate; unit='%s', date='%s'", unit, date)
        id = self.__ids[unit]
        marketData = self.__api.getCoinMarketDataById(id, date)
        ret = marketData['current_price']['chf']
        self.__rates[cacheKey] = ret

    def __loadIds(self):
        CoinGeckoCurrencyConverter.__log.info('Get ids')
        coins = self.__api.getCoinList()
        for coin in coins:
            symbol = coin['symbol']
            id = coin['id']
            self.__ids[symbol.upper()] = id
