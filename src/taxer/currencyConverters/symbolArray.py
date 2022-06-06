from .csvFileArray import CsvFileArray


class SymbolArray:
    def __init__(self, log, filePath, api):
        self.__fileArray = CsvFileArray(log, filePath)
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
        self.__fileArray.set(self.__api.getSymbols())
