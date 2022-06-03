from importlib import import_module


class CurrencyConverters:
    __fiat = ['EUR', 'USD']

    def __init__(self, config, cachePath):
        self.__config = config['currencyConverters']
        self.__converters = CurrencyConverters.__createConverters(self.__config, cachePath)
        self.__providers = {
            'AXN' : self.__converters['CCC'],
            'BTC' : self.__converters['CCC'],
            'ETH' : self.__converters['CCC'],
            'HEX' : self.__converters['CCC'],
            'HDRN': self.__converters['CCC'],
            'XRM' : self.__converters['CCC'],
            'XRP' : self.__converters['CCC'],
            'EUR' : self.__converters['ER'],
            'USD' : self.__converters['ER'],
            'USDC': self.__converters['CCC']
        }

    def load(self):
        for converter in self.__converters.values():
            converter.load()
        return self

    def store(self):
        for converter in self.__converters.values():
            converter.store()

    def exchangeRate(self, unit, date):
        provider = self.__providers[unit]
        rate = provider.exchangeRate(unit, date)
        return rate

    @staticmethod
    def isFiat(unit):
        isFiat = unit in CurrencyConverters.__fiat
        return isFiat

    @staticmethod
    def __createConverters(config, cachePath):
        ret = {}
        for configKey in config.keys():
            converterConfig = config[configKey]
            if ('disable' in converterConfig and converterConfig['disable']):
                continue
            className = configKey[0].upper() + configKey[1:]
            fullName = '.{}.{}CurrencyConverter.{}CurrencyConverter'.format(configKey, configKey, className)
            converterClass = CurrencyConverters.__importConverter(fullName)
            ret[converterConfig['id']] = converterClass(config, cachePath)
        return ret

    @staticmethod
    def __importConverter(path):
        modulePath, _, className = path.rpartition('.')
        mod = import_module(modulePath, __package__)
        return getattr(mod, className)
