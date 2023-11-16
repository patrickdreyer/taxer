from ...container import Container
from ...currencyConverters.currencyConverterFactory import CurrencyConverterFactory
from ...transactions.currency import Currency
from ..baseCurrency import BaseCurrency


class BananaCurrency(Currency):
    def __init__(self, container:Container, currency, mergentId, dateTime = None):
        if dateTime == None:
            self.__init__(container, currency, mergentId.mergentId, mergentId.dateTime)
        else:
            super().__init__(currency.unit, currency.amountRaw)
            self.__account = container['banana']['accounts'].get(currency.unit, mergentId)
            self.__baseCurrency = BaseCurrency(container, currency, dateTime)
            self.__isFiat = self.unit in container['config']['fiat']

    @property
    def account(self):
        return self.__account

    @property
    def baseCurrency(self):
        return self.__baseCurrency

    @property
    def isFiat(self):
        return self.__isFiat
