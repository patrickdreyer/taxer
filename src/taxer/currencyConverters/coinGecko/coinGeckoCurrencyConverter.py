import csv
from decimal import Decimal
import logging
import os

from .coinGeckoApi import CoinGeckoApi
from ..currencyConverter import CurrencyConverter


class CoinGeckoCurrencyConverter(CurrencyConverter):
    __idsFileName = 'CoinGeckoCurrency-Ids.csv'
    __ratesFileName = 'CoinGeckoCurrency-Rates.csv'

    __log = logging.getLogger(__name__)

    __ids = dict()
    __idsDirty = False
    __rates = dict()
    __ratesDirty = False

    def __init__(self, config, cachePath):
        self.__config = config['coinGecko']
        self.__cachePath = cachePath
        self.__api = CoinGeckoApi(self.__config)

    def exchangeRate(self, unit, date):
        cacheKey = '{0}{1}'.format(unit, date.strftime('%Y%m%d'))
        if not cacheKey in CoinGeckoCurrencyConverter.__rates:
            self.__fetchExchangeRate(unit, date, cacheKey)
        return Decimal(CoinGeckoCurrencyConverter.__rates[cacheKey])

    def load(self):
        CoinGeckoCurrencyConverter.__loadIds(self.__cachePath)
        CoinGeckoCurrencyConverter.__loadRates(self.__cachePath)

    def store(self):
        CoinGeckoCurrencyConverter.__storeIds(self.__cachePath)
        CoinGeckoCurrencyConverter.__storeRates(self.__cachePath)

    @staticmethod
    def __loadIds(cachePath):
        filePath = os.path.join(cachePath, CoinGeckoCurrencyConverter.__idsFileName)
        if not os.path.isfile(filePath):
            CoinGeckoCurrencyConverter.__log.info("Ids cache not present; filePath='%s'", filePath)
            return
        CoinGeckoCurrencyConverter.__log.info("Load ids cache; filePath='%s'", filePath)
        with open(filePath) as file:
            reader = csv.DictReader(file, dialect='unix')
            CoinGeckoCurrencyConverter.__ids = {row['unit']:row['id'] for row in reader}

    @staticmethod
    def __storeIds(cachePath):
        if not CoinGeckoCurrencyConverter.__idsDirty:
            CoinGeckoCurrencyConverter.__log.debug("No changes on ids cache")
            return
        filePath = os.path.join(cachePath, CoinGeckoCurrencyConverter.__idsFileName)
        CoinGeckoCurrencyConverter.__log.info("Store ids cache; filePath='%s'", filePath)
        with open(filePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['unit', 'id'])
            for unit, id in CoinGeckoCurrencyConverter.__ids.items():
                writer.writerow([unit, id])

    @staticmethod
    def __loadRates(cachePath):
        filePath = os.path.join(cachePath, CoinGeckoCurrencyConverter.__ratesFileName)
        if not os.path.isfile(filePath):
            CoinGeckoCurrencyConverter.__log.info("Rates cache not present; filePath='%s'", filePath)
            return
        CoinGeckoCurrencyConverter.__log.info("Load rates cache; filePath='%s'", filePath)
        with open(filePath) as file:
            reader = csv.DictReader(file, dialect='unix')
            CoinGeckoCurrencyConverter.__rates = {row['key']:Decimal(row['rate']) for row in reader}

    @staticmethod
    def __storeRates(cachePath):
        if not CoinGeckoCurrencyConverter.__ratesDirty:
            CoinGeckoCurrencyConverter.__log.debug("No changes on rates cache")
            return
        filePath = os.path.join(cachePath, CoinGeckoCurrencyConverter.__ratesFileName)
        CoinGeckoCurrencyConverter.__log.info("Store rates cache; filePath='%s'", filePath)
        with open(filePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['key', 'rate'])
            for key, rate in CoinGeckoCurrencyConverter.__rates.items():
                writer.writerow([key, rate])

    def __fetchExchangeRate(self, unit, date, cacheKey):
        CoinGeckoCurrencyConverter.__log.info("Fetch exchange rate; unit='%s', date='%s'", unit, date)
        id = self.__mapUnit2Id(unit)
        marketData = self.__api.getCoinMarketDataById(id, date)
        ret = marketData['current_price']['chf']
        CoinGeckoCurrencyConverter.__rates[cacheKey] = ret
        CoinGeckoCurrencyConverter.__ratesDirty = True

    def __mapUnit2Id(self, unit):
        if not unit in CoinGeckoCurrencyConverter.__ids:
            CoinGeckoCurrencyConverter.__log.info('Fetch unit to id map')
            coins = self.__api.getCoinList()
            for coin in coins:
                symbol = coin['symbol']
                id = coin['id']
                CoinGeckoCurrencyConverter.__ids[symbol.upper()] = id
            CoinGeckoCurrencyConverter.__idsDirty = True
        return CoinGeckoCurrencyConverter.__ids[unit]
