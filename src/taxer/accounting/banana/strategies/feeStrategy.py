import logging

from ....transactions.fee import Fee
from ..bananaStrategy import BananaStrategy


class FeeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, Fee)

    def transform(self, transaction):
        FeeStrategy.__log.debug("%s - Fee; %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount)
        c = self._currency(transaction.amount, transaction)
        #                              description, deposit,             withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
        yield self._book(transaction, ['Gebühr',    self._accounts.fees, c.account,  c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, ''])
