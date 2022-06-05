from .csvFileDict import CsvFileDict


class SymbolDict:
    def __init__(self, log, filePath, api):
        self.__api = api
        self.__fileDict = CsvFileDict(log, filePath, ['unit', 'id'])

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
        coins = self.__api.getSymbols()
        for coin in coins:
            self.__fileDict[coin['symbol'].upper()] = coin['id']
