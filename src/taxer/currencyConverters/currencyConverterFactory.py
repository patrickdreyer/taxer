from importlib import import_module


class CurrencyConverterFactory:
    __fiat = ['EUR', 'USD']

    @staticmethod
    def create(config, cachePath):
        ret = CurrencyConverterFactory(config, cachePath)
        ret.__createConverters()
        return ret

    def __init__(self, config, cachePath):
        self.__config = config['currencyConverters']
        self.__cachePath = cachePath

    def load(self):
        for converter in self.__converters.values():
            converter.load()
        return self

    def store(self):
        for converter in self.__converters.values():
            converter.store()

    def exchangeRate(self, symbol, date):
        for converter in self.__converters:
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
        for configKey in self.__config.keys():
            converterConfig = self.__config[configKey]
            if ('disable' in converterConfig and converterConfig['disable']):
                continue
            className = configKey[0].upper() + configKey[1:]
            fullName = '.{}.{}CurrencyConverter.{}CurrencyConverter'.format(configKey, configKey, className)
            converterClass = CurrencyConverterFactory.__importConverter(fullName)
            self.__converters[converterConfig['id']] = converterClass(self.__config, self.__cachePath)

    @staticmethod
    def __importConverter(path):
        modulePath, _, className = path.rpartition('.')
        mod = import_module(modulePath, __package__)
        return getattr(mod, className)
