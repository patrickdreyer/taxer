from importlib import import_module


class CurrencyConverters:
    __fiat = ['EUR', 'USD']

    def __init__(self, config, cachePath):
        self.__config = config['currencyConverters']
        self.__cachePath = cachePath

    def create(self):
        self.__converters = self.__createConverters()
        return self

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
        isFiat = unit in CurrencyConverters.__fiat
        return isFiat

    def __createConverters(self):
        ret = {}
        for configKey in self.__config.keys():
            converterConfig = self.__config[configKey]
            if ('disable' in converterConfig and converterConfig['disable']):
                continue
            className = configKey[0].upper() + configKey[1:]
            fullName = '.{}.{}CurrencyConverter.{}CurrencyConverter'.format(configKey, configKey, className)
            converterClass = CurrencyConverters.__importConverter(fullName)
            ret[converterConfig['id']] = converterClass(self.__config, self.__cachePath)
        return ret

    @staticmethod
    def __importConverter(path):
        modulePath, _, className = path.rpartition('.')
        mod = import_module(modulePath, __package__)
        return getattr(mod, className)
