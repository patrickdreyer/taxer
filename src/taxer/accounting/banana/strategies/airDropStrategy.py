import logging

from ....transactions.airDrop import AirDrop
from ..bananaStrategy import BananaStrategy


class AirDropStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, AirDrop)

    def transform(self, transaction):
        description = f"AirDrop; {transaction.amount.unit}"
        c = self._currency(transaction.amount, transaction)
        AirDropStrategy.__log.debug("%s - AirDrop; %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount)
        # air drop                     description, deposit,   withdrawal,            amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
        yield self._book(transaction, [description, c.account, '',                    c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, ''])
        # claim
        yield self._book(transaction, [description, '',        self._accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, ''])
