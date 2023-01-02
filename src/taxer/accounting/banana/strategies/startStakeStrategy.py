import logging

from ....transactions.startStake import StartStake
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class StartStakeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return isinstance(transaction, StartStake)

    def transform(self, transaction):
        description = '{} Stake; Start'.format(transaction.amount.unit)
        w = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        s = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, self.__accounts.staked, transaction.dateTime)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        StartStakeStrategy.__log.debug("%s - Stake start; %s", transaction.dateTime, transaction.amount)
        # withdrawal                                      description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield BananaStrategy._createBooking(transaction, [description, '',                   w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     w.costCenter.minus()])
        # stake
        yield BananaStrategy._createBooking(transaction, [description, s.account,            '',         s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount, '',     s.costCenter])
        # fee
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.fees, f.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])
