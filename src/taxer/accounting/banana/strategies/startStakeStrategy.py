import logging

from ....container import Container
from ....transactions.startStake import StartStake
from ..bananaStrategy import BananaStrategy


class StartStakeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, container:Container):
        super(StartStakeStrategy, self).__init__(container)
        self.__accounts = container['banana']['accounts']

    def doesTransform(self, transaction):
        return isinstance(transaction, StartStake)

    def transform(self, transaction):
        description = '{} Stake; Start'.format(transaction.amount.unit)
        w = self._currency(transaction.amount, transaction)
        s = self._currency(transaction.amount, self.__accounts.staked, transaction.dateTime)
        f = self._currency(transaction.fee, transaction)
        StartStakeStrategy.__log.debug("%s - Stake start; %s", transaction.dateTime, transaction.amount)
        # withdrawal                   description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
        yield self._book(transaction, [description, '',                   w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, ''])
        # stake
        yield self._book(transaction, [description, s.account,            '',         s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount, ''])
        # fee
        yield self._book(transaction, [description, self.__accounts.fees, f.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, ''])
