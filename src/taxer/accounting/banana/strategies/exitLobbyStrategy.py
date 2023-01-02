import logging

from ....transactions.exitLobby import ExitLobby
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class ExitLobbyStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return isinstance(transaction, ExitLobby)

    def transform(self, transaction):
        description = '{} Lobby; Exit'.format(transaction.lobby.unit)
        l = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.lobby, transaction.amount.unit, transaction.dateTime)
        d = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        ExitLobbyStrategy.__log.debug("%s - Lobby exit; %s -> %s", transaction.dateTime, transaction.lobby, transaction.amount)
        # lobby                                           description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield BananaStrategy._createBooking(transaction, [description, '',                   l.account,  l.amount, l.unit,   l.baseCurrency.exchangeRate, l.baseCurrency.amount, '',     l.costCenter.minus()])
        # deposit
        yield BananaStrategy._createBooking(transaction, [description, d.account,            '',         d.amount, d.unit,   d.baseCurrency.exchangeRate, d.baseCurrency.amount, '',     d.costCenter])
        # fee
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.fees, f.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])
