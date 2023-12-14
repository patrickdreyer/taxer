import logging

from ....transactions.reimbursement import Reimbursement
from ..bananaStrategy import BananaStrategy


class ReimbursementStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, Reimbursement)

    def transform(self, transaction):
        ReimbursementStrategy.__log.debug("%s - Reimbursement; %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount)
        c = self._currency(transaction.amount, transaction)
        #                              description,      deposit,   withdrawal,            amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
        yield self._book(transaction, ['Rückerstattung', c.account, self__accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, ''])
