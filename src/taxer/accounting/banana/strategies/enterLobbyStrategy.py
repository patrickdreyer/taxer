import logging

from ....transactions.enterLobby import EnterLobby
from ..bananaStrategy import BananaStrategy


class EnterLobbyStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, EnterLobby)

    def transform(self, transaction):
        description = '{} Lobby; Enter'.format(transaction.lobby)
        w = self._currency(transaction.amount, transaction)
        f = self._currency(transaction.fee, transaction)
        lAccount = self._accounts.get(transaction.amount.unit, transaction.lobby)
        EnterLobbyStrategy.__log.debug("%s - Lobby enter; %s, %s", transaction.dateTime, transaction.lobby, transaction.amount)
        # withdrawal                   description, deposit,             withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
        yield self._book(transaction, [description, '',                  w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, ''])
        # lobby
        yield self._book(transaction, [description, lAccount,            '',         w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, ''])
        # fee
        yield self._book(transaction, [description, self._accounts.fees, w.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, ''])
