import logging

from ....container import Container
from ....transactions.fee import Fee
from ..bananaStrategy import BananaStrategy


class FeeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, container:Container):
        super(FeeStrategy, self).__init__(container)
        self.__accounts = container['banana']['accounts']

    def doesTransform(self, transaction):
        return isinstance(transaction, Fee)

    def transform(self, transaction):
        FeeStrategy.__log.debug("%s - Fee; %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount)
        c = self._currency(transaction.amount, transaction)
        #                              description,     deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield self._book(transaction, ['Gebühr', self.__accounts.fees, c.account,  c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter.minus()])
