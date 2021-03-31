from .coinGecko import CoinGeckoCurrencyConverter
from .exchangeRatesApiIo import ExchangeRatesApiIo


class CurrencyConverter:
    __coinGecko = CoinGeckoCurrencyConverter()
    __exchangeRatesApiTo = ExchangeRatesApiIo()
    __providers = {
        'AXN' : __coinGecko,
        'BTC' : __coinGecko,
        'ETH' : __coinGecko,
        'HEX' : __coinGecko,
        'XRM' : __coinGecko,
        'XRP' : __coinGecko,
        'EUR' : __exchangeRatesApiTo,
        'USD' : __exchangeRatesApiTo,
        'USDC': __coinGecko
    }

    def exchangeRate(self, unit, date):
        provider = self.__providers[unit]
        return provider.exchangeRate(unit, date)
