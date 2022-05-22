from .coinGecko.coinGeckoCurrencyConverter import CoinGeckoCurrencyConverter
from .excelRates import ExcelRates


class CurrencyConverters:
    __fiat = ['EUR', 'USD']

    def __init__(self, config, cachePath):
        self.__config = config['currencyConverters']
        self.__converters = {
            'CG': CoinGeckoCurrencyConverter(self.__config, cachePath),
            'ER': ExcelRates(self.__config, cachePath)
        }
        self.__providers = {
            'AXN' : self.__converters['CG'],
            'BTC' : self.__converters['CG'],
            'ETH' : self.__converters['CG'],
            'HEX' : self.__converters['CG'],
            'HDRN': self.__converters['CG'],
            'XRM' : self.__converters['CG'],
            'XRP' : self.__converters['CG'],
            'EUR' : self.__converters['ER'],
            'USD' : self.__converters['ER'],
            'USDC': self.__converters['CG']
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
