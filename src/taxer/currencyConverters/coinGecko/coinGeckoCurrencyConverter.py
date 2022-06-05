from decimal import Decimal
import logging
import os

from .coinGeckoApi import CoinGeckoApi
from ..csvFileDict import CsvFileDict
from ..currencyConverter import CurrencyConverter


class CoinGeckoCurrencyConverter(CurrencyConverter):
    __symbols = [ 'AXN', 'BTC', 'ETH', 'HEX', 'HDRN', 'XRM', 'XRP', 'USDC' ]

    __log = logging.getLogger(__name__)

    def __init__(self, config, cachePath):
        self.__config = config['coinGecko']
        self.__api = CoinGeckoApi(self.__config)
        self.__ids = CsvFileDict(os.path.join(cachePath, self.__config['idsFileName']), ['unit', 'id'])
        self.__rates = CsvFileDict(os.path.join(cachePath, self.__config['ratesFileName']), ['key', 'rate'])

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
        return self.__symbols

    def exchangeRate(self, unit, date):
        cacheKey = '{0}{1}'.format(unit, date.strftime('%Y%m%d'))
        if not cacheKey in self.__rates():
            self.__fetchExchangeRate(unit, date, cacheKey)
        return Decimal(self.__rates[cacheKey])

    def __fetchExchangeRate(self, unit, date, cacheKey):
        CoinGeckoCurrencyConverter.__log.info("Fetch exchange rate; unit='%s', date='%s'", unit, date)
        id = self.__mapUnit2Id(unit)
        marketData = self.__api.getCoinMarketDataById(id, date)
        ret = marketData['current_price']['chf']
        self.__rates[cacheKey] = ret

    def __mapUnit2Id(self, unit):
        if not unit in self.__ids():
            CoinGeckoCurrencyConverter.__log.info('Fetch unit to id map')
            coins = self.__api.getCoinList()
            for coin in coins:
                symbol = coin['symbol']
                id = coin['id']
                self.__ids[symbol.upper()] = id
        return self.__ids[unit]
