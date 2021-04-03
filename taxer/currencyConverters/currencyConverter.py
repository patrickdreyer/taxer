from .coinGecko import CoinGeckoCurrencyConverter
from .excelRates import ExcelRates


class CurrencyConverter:
    __coinGecko = CoinGeckoCurrencyConverter()
    __fiat = ['EUR', 'USD']

    def __init__(self, path):
        self.__excelRates = ExcelRates(path)
        self.__providers = {
            'AXN' : self.__coinGecko,
            'BTC' : self.__coinGecko,
            'ETH' : self.__coinGecko,
            'HEX' : self.__coinGecko,
            'XRM' : self.__coinGecko,
            'XRP' : self.__coinGecko,
            'EUR' : self.__excelRates,
            'USD' : self.__excelRates,
            'USDC': self.__coinGecko
        }

    def exchangeRate(self, unit, date):
        provider = self.__providers[unit]
        rate = provider.exchangeRate(unit, date)
        return rate

    @staticmethod
    def isFiat(unit):
        return unit in CurrencyConverter.__fiat
