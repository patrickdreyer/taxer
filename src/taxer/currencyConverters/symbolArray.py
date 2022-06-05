import logging

from .csvFileArray import CsvFileArray


class SymbolArray:
    __log = logging.getLogger(__name__)

    def __init__(self, filePath, api):
        self.__fileArray = CsvFileArray(filePath)
        self.__api = api

    def load(self):
        if not self.__fileArray.load():
            self.__loadIds()

    def store(self):
        self.__fileArray.store()

    @property
    def symbols(self):
        return self.__fileArray()

    def map(self, symbol):
        return symbol

    def __loadIds(self):
        SymbolArray.__log.info('Get symbols')
        self.__fileArray.set(self.__api.getSymbols())
