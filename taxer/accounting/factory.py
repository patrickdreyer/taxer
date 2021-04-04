from .banana.accounting import BananaAccounting


class AccountingFactory:
    def __init__(self, currencyConverters):
        self.__currencyConverters = currencyConverters

    def create(self, name):
        return BananaAccounting(self.__currencyConverters)
