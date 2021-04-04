from .coinGecko import CoinGeckoCurrencyConverter
from .excelRates import ExcelRates


class CurrencyConverters:
    __fiat = ['EUR', 'USD']
    __converters = {
        'CG': CoinGeckoCurrencyConverter(),
        'ER': ExcelRates()
    }
    __providers = {
        'AXN' : __converters['CG'],
        'BTC' : __converters['CG'],
        'ETH' : __converters['CG'],
        'HEX' : __converters['CG'],
        'XRM' : __converters['CG'],
        'XRP' : __converters['CG'],
        'EUR' : __converters['ER'],
        'USD' : __converters['ER'],
        'USDC': __converters['CG']
    }

    def exchangeRate(self, unit, date):
        provider = self.__providers[unit]
        rate = provider.exchangeRate(unit, date)
        return rate

    def load(self, path):
        for converter in CurrencyConverters.__converters.values():
            converter.load(path)
        return self

    def store(self, path):
        for converter in CurrencyConverters.__converters.values():
            converter.store(path)

    @staticmethod
    def isFiat(unit):
        return unit in CurrencyConverters.__fiat
