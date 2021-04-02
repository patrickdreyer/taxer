from ..currencyConverters.currencyConverter import CurrencyConverter
from .banana.accounting import BananaAccounting


class AccountingFactory:
    __currencyConverter = None

    def __init__(self, currencyConverter):
        self.__currencyConverter = currencyConverter

    def create(self, name):
        return BananaAccounting(self.__currencyConverter)
