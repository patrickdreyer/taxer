import logging

from ....transactions.payment import Payment
from ..bananaStrategy import BananaStrategy


class PaymentStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, Payment)

    def transform(self, transaction):
        PaymentStrategy.__log.debug("%s - Payment; %s, %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount, transaction.note)
        description = f'Bezahlung; {transaction.note}'
        w = self._currency(transaction.amount, transaction)
        if w.amount > 0:
            # amount                       description, deposit,               withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
            yield self._book(transaction, [description, self._accounts.equity, w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '', transaction.note])
        f = self._currency(transaction.fee, transaction)
        if f.amount > 0:
            # fee
            yield self._book(transaction, [description, self._accounts.fees,   w.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, ''])
