import logging

from ....transactions.endStake import EndStake
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class EndStakeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return isinstance(transaction, EndStake)

    def transform(self, transaction):
        description = '{} Stake; End'.format(transaction.amount.unit)
        u = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, self.__accounts.staked, transaction.dateTime)
        d = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.total, transaction)
        i = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.interest, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        EndStakeStrategy.__log.debug("%s - Stake end; %s", transaction.dateTime, transaction.amount)
        # deposit                                         description, deposit,              withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield BananaStrategy._createBooking(transaction, [description, d.account,            '',                     d.amount, d.unit,   d.baseCurrency.exchangeRate, d.baseCurrency.amount, '',     d.costCenter])
        # unstake
        yield BananaStrategy._createBooking(transaction, [description, '',                   u.account,              u.amount, u.unit,   u.baseCurrency.exchangeRate, u.baseCurrency.amount, '',     u.costCenter.minus()])
        # interest
        yield BananaStrategy._createBooking(transaction, [description, '',                   self.__accounts.equity, i.amount, i.unit,   i.baseCurrency.exchangeRate, i.baseCurrency.amount, '',     ''])
        # fee
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.fees, f.account,              f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])
