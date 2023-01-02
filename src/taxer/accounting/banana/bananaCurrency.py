from ...currencyConverters.currencyConverterFactory import CurrencyConverterFactory
from ...transactions.currency import Currency
from ..baseCurrency import BaseCurrency
from ..costCenter import CostCenter


class BananaCurrency(Currency):
    def __init__(self, accounts, currencyConverters, currency, mergentId, dateTime = None):
        if dateTime == None:
            self.__init__(accounts, currencyConverters, currency, mergentId.mergentId, mergentId.dateTime)
        else:
            super().__init__(currency.unit, currency.amountRaw)
            self.__account = accounts.get(currency.unit, mergentId)
            self.__baseCurrency = BaseCurrency(currencyConverters, currency, dateTime)
            self.__costCenter = CostCenter(mergentId, currency)

    @property
    def account(self):
        return self.__account

    @property
    def baseCurrency(self):
        return self.__baseCurrency

    @property
    def costCenter(self):
        return self.__costCenter

    @property
    def isFiat(self):
        return CurrencyConverterFactory.isFiat(self.unit)
