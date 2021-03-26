from ..currencyConverters.coinGecko import CoinGeckoCurrencyConverter
from .banana.accounting import BananaAccounting


class AccountingFactory:
    __currencyConverter = None

    def __init__(self):
        self.__currencyConverter = CoinGeckoCurrencyConverter()

    def create(self, name):
        return BananaAccounting(self.__currencyConverter)
