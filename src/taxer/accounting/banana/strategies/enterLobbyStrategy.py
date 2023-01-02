import logging

from ....transactions.enterLobby import EnterLobby
from ...costCenter import CostCenter
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class EnterLobbyStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return isinstance(transaction, EnterLobby)

    def transform(self, transaction):
        description = '{} Lobby; Enter'.format(transaction.lobby)
        w = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        lAccount = self.__accounts.get(transaction.amount.unit, transaction.lobby)
        lCostCenter = CostCenter(transaction.lobby, transaction.amount)
        EnterLobbyStrategy.__log.debug("%s - Lobby enter; %s, %s", transaction.dateTime, transaction.lobby, transaction.amount)
        # withdrawal                                      description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield BananaStrategy._createBooking(transaction, [description, '',                   w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     w.costCenter.minus()])
        # lobby
        yield BananaStrategy._createBooking(transaction, [description, lAccount,             '',         w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     lCostCenter])
        # fee
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.fees, w.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     w.costCenter.minus()])
