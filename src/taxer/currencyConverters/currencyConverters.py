from .coinGecko.coinGeckoCurrencyConverter import CoinGeckoCurrencyConverter
from .cryptoCurrencyChart.cryptoCurrencyChartCurrencyConverter import CryptoCurrencyChartCurrencyConverter
from .excelRates import ExcelRates


class CurrencyConverters:
    __fiat = ['EUR', 'USD']

    def __init__(self, config, cachePath):
        self.__config = config['currencyConverters']
        self.__converters = {
            #'CG' : CoinGeckoCurrencyConverter(self.__config, cachePath),
            'CCC': CryptoCurrencyChartCurrencyConverter(self.__config, cachePath),
            'ER' : ExcelRates(self.__config, cachePath)
        }
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
