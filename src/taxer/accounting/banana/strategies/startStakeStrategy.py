import logging

from ....transactions.startStake import StartStake
from ..bananaStrategy import BananaStrategy


class StartStakeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, StartStake)

    def transform(self, transaction):
        description = '{} Stake; Start {}'.format(transaction.amount.unit, transaction.stakeId)
        w = self._currency(transaction.amount, transaction)
        s = self._currency(transaction.amount, self._accounts.staked, transaction.dateTime)
        f = self._currency(transaction.fee, transaction)
        StartStakeStrategy.__log.debug("%s - Stake start; %s, %s", transaction.stakeId, transaction.dateTime, transaction.amount)
        # withdrawal                   description, deposit,             withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
        yield self._book(transaction, [description, '',                  w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, ''])
        # stake
        yield self._book(transaction, [description, s.account,           '',         s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount, ''])
        # fee
        yield self._book(transaction, [description, self._accounts.fees, f.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, ''])
