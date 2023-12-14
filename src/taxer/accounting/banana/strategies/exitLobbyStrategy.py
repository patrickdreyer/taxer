import logging

from ....transactions.exitLobby import ExitLobby
from ..bananaStrategy import BananaStrategy


class ExitLobbyStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, ExitLobby)

    def transform(self, transaction):
        description = '{} Lobby; Exit'.format(transaction.lobby.unit)
        l = self._currency(transaction.lobby, transaction.amount.unit, transaction.dateTime)
        d = self._currency(transaction.amount, transaction)
        f = self._currency(transaction.fee, transaction)
        ExitLobbyStrategy.__log.debug("%s - Lobby exit; %s -> %s", transaction.dateTime, transaction.lobby, transaction.amount)
        # lobby                        description, deposit,             withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
        yield self._book(transaction, [description, '',                  l.account,  l.amount, l.unit,   l.baseCurrency.exchangeRate, l.baseCurrency.amount, ''])
        # deposit
        yield self._book(transaction, [description, d.account,           '',         d.amount, d.unit,   d.baseCurrency.exchangeRate, d.baseCurrency.amount, ''])
        # fee
        yield self._book(transaction, [description, self._accounts.fees, f.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, ''])
