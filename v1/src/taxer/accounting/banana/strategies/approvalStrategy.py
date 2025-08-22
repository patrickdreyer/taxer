import logging

from ....transactions.approval import Approval
from ..bananaStrategy import BananaStrategy


class ApprovalStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, Approval)

    def transform(self, transaction):
        ApprovalStrategy.__log.debug("%s - Approval; %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount)
        c = self._currency(transaction.amount, transaction)
        #                              description, deposit,             withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
        yield self._book(transaction, ['Freigabe',  self._accounts.fees, c.account,  c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, ''])
