import logging

from ....container import Container
from ....transactions.mint import Mint
from ..bananaStrategy import BananaStrategy


class MintStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, container:Container):
        super(MintStrategy, self).__init__(container)
        self.__accounts = container['banana']['accounts']

    def doesTransform(self, transaction):
        return isinstance(transaction, Mint)

    def transform(self, transaction):
        description = '{} Mint'.format(transaction.amount.unit)
        c = self._currency(transaction.amount, transaction)
        f = self._currency(transaction.fee, transaction)
        MintStrategy.__log.debug("%s - Mint; %s", transaction.dateTime, transaction.amount)
        # deposit                      description, deposit,              withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield self._book(transaction, [description, c.account,            '',                     c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])
        # claim
        yield self._book(transaction, [description, '',                   self.__accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     ''])
        # fee
        yield self._book(transaction, [description, self.__accounts.fees, f.account,              f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])
