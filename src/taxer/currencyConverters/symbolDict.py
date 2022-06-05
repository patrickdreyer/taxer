import logging


from .csvFileDict import CsvFileDict


class SymbolDict:
    __log = logging.getLogger(__name__)

    def __init__(self, filePath, api):
        self.__fileDict = CsvFileDict(filePath, ['unit', 'id'])
        self.__api = api

    def load(self):
        if not self.__fileDict.load():
            self.__loadIds()

    def store(self):
        self.__fileDict.store()

    @property
    def symbols(self):
        return self.__fileDict().keys()

    def map(self, symbol):
        return self.__fileDict[symbol]

    def __loadIds(self):
        SymbolDict.__log.info('Get ids')
        coins = self.__api.getSymbols()
        for coin in coins:
            self.__fileDict[coin['symbol'].upper()] = coin['id']
