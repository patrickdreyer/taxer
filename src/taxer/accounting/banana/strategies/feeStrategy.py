import logging

from ....transactions.fee import Fee
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class FeeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return isinstance(transaction, Fee)

    def transform(self, transaction):
        FeeStrategy.__log.debug("%s - Fee; %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount)
        c = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        #                                                 description,     deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield BananaStrategy._createBooking(transaction, ['Gebühr', self.__accounts.fees, c.account,  c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter.minus()])
