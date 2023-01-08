from ..container import Container
from ..pluginLoader import PluginLoader


class CurrencyConverterFactory:
    __fiat = ['EUR', 'USD']

    @staticmethod
    def create(container:Container):
        ret = CurrencyConverterFactory(container)
        ret.__createConverters()
        return ret

    def __init__(self, container:Container):
        self.__container = container

    def load(self):
        for converter in self.__converters.values():
            converter.load()
        return self

    def store(self):
        for converter in self.__converters.values():
            converter.store()

    def exchangeRate(self, symbol, date):
        for converter in  self.__converters.values():
            if symbol in converter.symbols:
                rate = converter.exchangeRate(symbol, date)
                return rate
        raise KeyError("Symbol not supported by currency converters; symbol='{}'".format(symbol))

    @staticmethod
    def isFiat(unit):
        isFiat = unit in CurrencyConverterFactory.__fiat
        return isFiat

    def __createConverters(self):
        self.__converters = {}
        for converter in PluginLoader.loadByConfig(self.__container['config']['currencyConverters'], __package__ + '.{}.{}CurrencyConverter.{}CurrencyConverter', lambda config, clss : clss(self.__container, config)):
            self.__converters[converter.id] = converter
