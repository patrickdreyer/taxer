import logging

from ....container import Container
from ....transactions.reimbursement import Reimbursement
from ..bananaStrategy import BananaStrategy


class ReimbursementStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, container:Container):
        super(ReimbursementStrategy, self).__init__(container)
        self.__accounts = container['banana']['accounts']

    def doesTransform(self, transaction):
        return isinstance(transaction, Reimbursement)

    def transform(self, transaction):
        ReimbursementStrategy.__log.debug("%s - Reimbursement; %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount)
        c = self._currency(transaction.amount, transaction)
        #                              description,      deposit,   withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield self._book(transaction, ['Rückerstattung', c.account, self.__accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])
