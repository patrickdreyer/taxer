from ..container import container
from ..pluginLoader import PluginLoader


class CurrencyConverterFactory:
    @staticmethod
    def create():
        ret = CurrencyConverterFactory()
        ret.__createConverters()
        return ret

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

    def __createConverters(self):
        self.__converters = {}
        for converter in PluginLoader.loadByConfig(container['config']['currencyConverters'], __package__ + '.{}.{}CurrencyConverter.{}CurrencyConverter', lambda config, clss : clss(config)):
            self.__converters[converter.id] = converter
