import logging

from ....transactions.endStake import EndStake
from ..bananaStrategy import BananaStrategy


class EndStakeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, EndStake)

    def transform(self, transaction):
        description = '{} Stake; End {}'.format(transaction.amount.unit, transaction.stakeId)
        u = self._currency(transaction.amount, self._accounts.staked, transaction.dateTime)
        d = self._currency(transaction.total, transaction)
        i = self._currency(transaction.interest, transaction)
        f = self._currency(transaction.fee, transaction)
        EndStakeStrategy.__log.debug("%s - Stake end; %s, %s", transaction.stakeId, transaction.dateTime, transaction.amount)
        # deposit                      description, deposit,             withdrawal,            amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
        yield self._book(transaction, [description, d.account,           '',                    d.amount, d.unit,   d.baseCurrency.exchangeRate, d.baseCurrency.amount, ''])
        # unstake
        yield self._book(transaction, [description, '',                  u.account,             u.amount, u.unit,   u.baseCurrency.exchangeRate, u.baseCurrency.amount, ''])
        # interest
        yield self._book(transaction, [description, '',                  self._accounts.equity, i.amount, i.unit,   i.baseCurrency.exchangeRate, i.baseCurrency.amount, ''])
        # fee
        yield self._book(transaction, [description, self._accounts.fees, f.account,             f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, ''])

        # interest                    description, amount,   currency, exchangeRate,                baseCurrencyAmount
        self._interest(transaction, ['Staking',    i.amount, i.unit,   i.baseCurrency.exchangeRate, i.baseCurrency.amount])
