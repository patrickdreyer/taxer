import csv
from decimal import Decimal
import logging
import os
from pycoingecko import CoinGeckoAPI

from .currencyConverter import CurrencyConverter


class CoinGeckoCurrencyConverter(CurrencyConverter):
    __idsFileName = 'CoinGecko-Ids.csv'
    __ratesFileName = 'CoinGecko-Rates.csv'

    __log = logging.getLogger(__name__)

    __api = CoinGeckoAPI()
    __ids = dict()
    __idsDirty = False
    __rates = dict()
    __ratesDirty = False

    def exchangeRate(self, unit, date):
        cacheKey = '{0}{1}'.format(unit, date.strftime('%Y%m%d'))
        if not cacheKey in CoinGeckoCurrencyConverter.__rates:
            CoinGeckoCurrencyConverter.__fetchExchangeRate(unit, date, cacheKey)
        return CoinGeckoCurrencyConverter.__rates[cacheKey]

    def load(self, cachePath):
        CoinGeckoCurrencyConverter.__loadIds(cachePath)
        CoinGeckoCurrencyConverter.__loadRates(cachePath)

    def store(self, cachePath):
        CoinGeckoCurrencyConverter.__storeIds(cachePath)
        CoinGeckoCurrencyConverter.__storeRates(cachePath)

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

    @staticmethod
    def __fetchExchangeRate(unit, date, cacheKey):
        CoinGeckoCurrencyConverter.__log.info("Fetch exchange rate; unit='%s', date='%s'", unit, date)
        id = CoinGeckoCurrencyConverter.__mapUnit2Id(unit)
        response = CoinGeckoCurrencyConverter.__api.get_coin_history_by_id(id, date.strftime('%d-%m-%Y'))
        ret = response['market_data']['current_price']['chf']
        CoinGeckoCurrencyConverter.__rates[cacheKey] = ret
        CoinGeckoCurrencyConverter.__ratesDirty = True

    @staticmethod
    def __mapUnit2Id(unit):
        if not unit in CoinGeckoCurrencyConverter.__ids:
            CoinGeckoCurrencyConverter.__log.info('Fetch unit to id map')
            coins = CoinGeckoCurrencyConverter.__api.get_coins_list()
            for coin in coins:
                symbol = coin['symbol']
                id = coin['id']
                CoinGeckoCurrencyConverter.__ids[symbol.upper()] = id
            CoinGeckoCurrencyConverter.__idsDirty = True
        return CoinGeckoCurrencyConverter.__ids[unit]
