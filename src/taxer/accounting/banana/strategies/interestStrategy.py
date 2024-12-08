import logging

from ....transactions.interest import Interest
from ..bananaStrategy import BananaStrategy


class InterestStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, Interest)

    def transform(self, transaction):
        c = self._currency(transaction.amount, transaction)
        InterestStrategy.__log.debug("%s - Interest; %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount)
        # interest                    description, amount,   currency, exchangeRate,                baseCurrencyAmount
        self._interest(transaction, ['Interest',   c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount])
