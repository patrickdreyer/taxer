import logging

from ....transactions.mint import Mint
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class MintStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return isinstance(transaction, Mint)

    def transform(self, transaction):
        description = '{} Mint'.format(transaction.amount.unit)
        c = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        MintStrategy.__log.debug("%s - Mint; %s", transaction.dateTime, transaction.amount)
        # deposit                                         description, deposit,              withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield BananaStrategy._createBooking(transaction, [description, c.account,            '',                     c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])
        # claim
        yield BananaStrategy._createBooking(transaction, [description, '',                   self.__accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     ''])
        # fee
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.fees, f.account,              f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])
