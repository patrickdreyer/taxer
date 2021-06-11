class BaseCurrency:
    def __init__(self, currencyConverters, currency, dateTime):
        self.__exchangeRate = currencyConverters.exchangeRate(currency.unit, dateTime.date())
        self.__amount = round(currency.amount * self.__exchangeRate, 2)

    @property
    def exchangeRate(self):
        return self.__exchangeRate

    @property
    def amount(self):
        return self.__amount
