from ...container import container
from ...currencyConverters.currencyConverterFactory import CurrencyConverterFactory
from ...transactions.currency import Currency
from ..baseCurrency import BaseCurrency


class BananaCurrency(Currency):
    def __init__(self, currency, mergentId, dateTime = None):
        if dateTime == None:
            self.__init__(currency, mergentId.mergentId, mergentId.dateTime)
        else:
            super().__init__(currency.unit, currency.amountRaw)
            self.__account = container['banana']['accounts'].get(currency.unit, mergentId)
            self.__baseCurrency = BaseCurrency(currency, dateTime)
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
