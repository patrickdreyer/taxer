import logging

from ....transactions.mint import Mint
from ..bananaStrategy import BananaStrategy


class MintStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, Mint)

    def transform(self, transaction):
        description = '{} Mint'.format(transaction.amount.unit)
        c = self._currency(transaction.amount, transaction)
        f = self._currency(transaction.fee, transaction)
        MintStrategy.__log.debug("%s - Mint; %s", transaction.dateTime, transaction.amount)
        # deposit                      description, deposit,             withdrawal,            amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
        yield self._book(transaction, [description, c.account,           '',                    c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, ''])
        # claim
        yield self._book(transaction, [description, '',                  self._accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, ''])
        # fee
        yield self._book(transaction, [description, self._accounts.fees, f.account,             f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, ''])
