from .banana.accounting import BananaAccounting


class AccountingFactory:
    def __init__(self, config, currencyConverters):
        self.__config = config
        self.__currencyConverters = currencyConverters

    def create(self, name):
        return BananaAccounting(self.__config, self.__currencyConverters)
