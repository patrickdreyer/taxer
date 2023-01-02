import logging

from ....transactions.covesting import Covesting
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class CovestingStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return isinstance(transaction, Covesting)

    def transform(self, transaction):
        # loss/gain
        a = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        # entry fee
        e = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.entryFee, transaction)
        # exit fee
        x = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.exitFee, transaction)
        #                                                     description,                                     deposit,                withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,   shares, costCenter1
        if e.amount > 0:
            yield BananaStrategy._createBooking(transaction, ['{} - Startgebühren'.format(transaction.trader), self.__accounts.fees,   e.account,              e.amount, e.unit,   e.baseCurrency.exchangeRate, e.baseCurrency.amount, '',    e.costCenter.minus()])
        if a.amountRaw >= 0:
            CovestingStrategy.__log.debug("%s - Covesting gain; %s, %s, %s, %s", transaction.dateTime, transaction.mergentId, transaction.trader, a, transaction.note)
            yield BananaStrategy._createBooking(transaction, ['{} - Gewinn'.format(transaction.trader),        a.account,              self.__accounts.equity, a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, '',    a.costCenter])
        else:
            CovestingStrategy.__log.debug("%s - Covesting loss; %s, %s, %s, %s", transaction.dateTime, transaction.mergentId, transaction.trader, a, transaction.note)
            yield BananaStrategy._createBooking(transaction, ['{} - Verlust'.format(transaction.trader),       self.__accounts.equity, a.account,              a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, '',    a.costCenter.minus()])
        if x.amount > 0:
            yield BananaStrategy._createBooking(transaction, ['{} - Gebühren'.format(transaction.trader),      self.__accounts.fees,   x.account,              x.amount, x.unit,   x.baseCurrency.exchangeRate, x.baseCurrency.amount, '',    x.costCenter.minus()])
