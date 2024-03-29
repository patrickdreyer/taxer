from ..container import container


class BaseCurrency:
    def __init__(self, currency, dateTime):
        self.__exchangeRate = container['currencyConverters'].exchangeRate(currency.unit, dateTime.date())
        self.__amount = round(currency.amount * self.__exchangeRate, 16)

    @property
    def exchangeRate(self):
        return self.__exchangeRate

    @property
    def amount(self):
        return self.__amount
