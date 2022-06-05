class DummySymbolMapper:
    def __init__(self, api):
        self.__api = api

    def load(self):
        self.__symbols = self.__api.getSymbols()

    def store(self):
        pass

    @property
    def symbols(self):
        return self.__symbols

    def map(self, symbol):
        return symbol
