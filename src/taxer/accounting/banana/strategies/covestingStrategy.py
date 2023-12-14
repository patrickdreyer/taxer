import logging

from ....transactions.covesting import Covesting
from ..bananaStrategy import BananaStrategy


class CovestingStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, Covesting)

    def transform(self, transaction):
        # loss/gain
        a = self._currency(transaction.amount, transaction)
        # entry fee
        e = self._currency(transaction.entryFee, transaction)
        # exit fee
        x = self._currency(transaction.exitFee, transaction)
        #                                  description,                                     deposit,               withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
        if e.amount > 0:
            yield self._book(transaction, ['{} - Startgebühren'.format(transaction.trader), self._accounts.fees,   e.account,              e.amount, e.unit,   e.baseCurrency.exchangeRate, e.baseCurrency.amount, ''])
        if a.amountRaw >= 0:
            CovestingStrategy.__log.debug("%s - Covesting gain; %s, %s, %s, %s", transaction.dateTime, transaction.mergentId, transaction.trader, a, transaction.note)
            yield self._book(transaction, ['{} - Gewinn'.format(transaction.trader),        a.account,             self._accounts.equity, a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, ''])
        else:
            CovestingStrategy.__log.debug("%s - Covesting loss; %s, %s, %s, %s", transaction.dateTime, transaction.mergentId, transaction.trader, a, transaction.note)
            yield self._book(transaction, ['{} - Verlust'.format(transaction.trader),       self._accounts.equity, a.account,              a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, ''])
        if x.amount > 0:
            yield self._book(transaction, ['{} - Gebühren'.format(transaction.trader),      self._accounts.fees,   x.account,              x.amount, x.unit,   x.baseCurrency.exchangeRate, x.baseCurrency.amount, ''])
