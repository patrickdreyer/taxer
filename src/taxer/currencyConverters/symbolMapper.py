import logging


class SymbolMapper:
    __log = logging.getLogger(__name__)

    def __init__(self, fileDict, api):
        self.__fileDict = fileDict
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
        SymbolMapper.__log.info('Get ids')
        coins = self.__api.getSymbols()
        for coin in coins:
            self.__fileDict[coin['symbol'].upper()] = coin['id']
