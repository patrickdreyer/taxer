import csv
from decimal import Decimal
import logging
import os

from .cryptoCurrencyChartApi import CryptoCurrencyChartApi
from ..currencyConverter import CurrencyConverter


class CryptoCurrencyChartCurrencyConverter(CurrencyConverter):
    __log = logging.getLogger(__name__)

    __ids = dict()
    __idsDirty = False
    __rates = dict()
    __ratesDirty = False

    def __init__(self, config, cachePath):
        self.__config = config['cryptoCurrencyChart']
        self.__cachePath = cachePath
        self.__api = CryptoCurrencyChartApi(self.__config)

    def exchangeRate(self, unit, date):
        cacheKey = '{0}{1}'.format(unit, date.strftime('%Y%m%d'))
        if not cacheKey in CryptoCurrencyChartCurrencyConverter.__rates:
            self.__fetchExchangeRate(unit, date, cacheKey)
        return Decimal(CryptoCurrencyChartCurrencyConverter.__rates[cacheKey])

    def load(self):
        self.__loadIds()
        self.__loadRates()

    def store(self):
        self.__storeIds()
        self.__storeRates()

    def __loadIds(self):
        filePath = os.path.join(self.__cachePath, self.__config['idsFileName'])
        if not os.path.isfile(filePath):
            CryptoCurrencyChartCurrencyConverter.__log.info("Ids cache not present; filePath='%s'", filePath)
            return
        CryptoCurrencyChartCurrencyConverter.__log.info("Load ids cache; filePath='%s'", filePath)
        with open(filePath) as file:
            reader = csv.DictReader(file, dialect='unix')
            CryptoCurrencyChartCurrencyConverter.__ids = {row['unit']:row['id'] for row in reader}

    def __storeIds(self):
        if not CryptoCurrencyChartCurrencyConverter.__idsDirty:
            CryptoCurrencyChartCurrencyConverter.__log.debug("No changes on ids cache")
            return
        filePath = os.path.join(self.__cachePath, self.__config['idsFileName'])
        CryptoCurrencyChartCurrencyConverter.__log.info("Store ids cache; filePath='%s'", filePath)
        with open(filePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['unit', 'id'])
            for unit, id in CryptoCurrencyChartCurrencyConverter.__ids.items():
                writer.writerow([unit, id])

    def __loadRates(self):
        filePath = os.path.join(self.__cachePath, self.__config['ratesFileName'])
        if not os.path.isfile(filePath):
            CryptoCurrencyChartCurrencyConverter.__log.info("Rates cache not present; filePath='%s'", filePath)
            return
        CryptoCurrencyChartCurrencyConverter.__log.info("Load rates cache; filePath='%s'", filePath)
        with open(filePath) as file:
            reader = csv.DictReader(file, dialect='unix')
            CryptoCurrencyChartCurrencyConverter.__rates = {row['key']:Decimal(row['rate']) for row in reader}

    def __storeRates(self):
        if not CryptoCurrencyChartCurrencyConverter.__ratesDirty:
            CryptoCurrencyChartCurrencyConverter.__log.debug("No changes on rates cache")
            return
        filePath = os.path.join(self.__cachePath, self.__config['ratesFileName'])
        CryptoCurrencyChartCurrencyConverter.__log.info("Store rates cache; filePath='%s'", filePath)
        with open(filePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['key', 'rate'])
            for key, rate in CryptoCurrencyChartCurrencyConverter.__rates.items():
                writer.writerow([key, rate])

    def __fetchExchangeRate(self, unit, date, cacheKey):
        CryptoCurrencyChartCurrencyConverter.__log.info("Fetch exchange rate; unit='%s', date='%s'", unit, date)
        id = self.__mapUnit2Id(unit)
        coin = self.__api.getCoinMarketDataById(id, date)
        ret = coin['price']
        CryptoCurrencyChartCurrencyConverter.__rates[cacheKey] = ret
        CryptoCurrencyChartCurrencyConverter.__ratesDirty = True

    def __mapUnit2Id(self, unit):
        if not unit in CryptoCurrencyChartCurrencyConverter.__ids:
            CryptoCurrencyChartCurrencyConverter.__log.info('Fetch unit to id map')
            coins = self.__api.getCoinList()
            for coin in coins:
                symbol = coin['symbol']
                id = coin['id']
                CryptoCurrencyChartCurrencyConverter.__ids[symbol.upper()] = id
            CryptoCurrencyChartCurrencyConverter.__idsDirty = True
        return CryptoCurrencyChartCurrencyConverter.__ids[unit]
