import logging

from ....container import Container
from ....transactions.marginTrade import MarginTrade
from ..bananaStrategy import BananaStrategy


class MarginTradeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, container:Container):
        super(MarginTradeStrategy, self).__init__(container)
        self.__accounts = container['banana']['accounts']

    def doesTransform(self, transaction):
        return isinstance(transaction, MarginTrade)

    def transform(self, transaction):
        # gain/loss
        a = self._currency(transaction.amount, transaction)
        # entry fee
        e = self._currency(transaction.entryFee, transaction)
        # exit fee
        x = self._currency(transaction.exitFee, transaction)
        #                                  description,               deposit,                withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,   shares
        if e.amount > 0:
            yield self._book(transaction, ['Margin Trade - Einstieg', self.__accounts.fees,   e.account,              e.amount, e.unit,   e.baseCurrency.exchangeRate, e.baseCurrency.amount, ''])
        if a.amountRaw >= 0:
            MarginTradeStrategy.__log.debug("%s - Margin gain; %s, %s", transaction.dateTime, transaction.mergentId, a)
            yield self._book(transaction, ['Margin Trade - Gewinn',   a.account,              self.__accounts.equity, a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, ''])
        else:
            MarginTradeStrategy.__log.debug("%s - Margin loss; %s, %s", transaction.dateTime, transaction.mergentId, a)
            yield self._book(transaction, ['Margin Trade - Verlust',  self.__accounts.equity, a.account,              a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, ''])
        yield self._book(transaction,     ['Margin Trade - Ausstieg', self.__accounts.fees,   a.account,              x.amount, a.unit,   x.baseCurrency.exchangeRate, x.baseCurrency.amount, ''])
