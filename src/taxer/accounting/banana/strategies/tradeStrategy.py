import logging

from ....transactions.buyTrade import BuyTrade
from ....transactions.sellTrade import SellTrade
from ....transactions.trade import Trade
from ..bananaStrategy import BananaStrategy


class TradeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return issubclass(type(transaction), Trade)

    def transform(self, transaction):
        sell = self._currency(transaction.sell, transaction)
        buy = self._currency(transaction.buy, transaction)
        fee = self._currency(transaction.fee, transaction)
        if isinstance(transaction, BuyTrade):
            yield from self.__transformBuy(transaction, sell, buy, fee)
        elif isinstance(transaction, SellTrade):
            yield from self.__transformSell(transaction, sell, buy, fee)

    def __transformBuy(self, transaction, s, b, f):
        TradeStrategy.__log.debug("%s - Buy; %s, %s", transaction.dateTime, transaction.mergentId, b)
        description = 'Kauf; {0}'.format(transaction.buy.unit)
        # fiat                         description, debit,                   credit,                  amount,   currency, exchangeRate,                baseCurrencyAmount,    shares
        yield self._book(transaction, [description, self._accounts.transfer, s.account,               s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount, ''])
        # crypto
        yield self._book(transaction, [description, b.account,               self._accounts.transfer, b.amount, b.unit,   b.baseCurrency.exchangeRate, b.baseCurrency.amount, ''])
        # fee
        yield self._book(transaction, [description, self._accounts.fees,     s.account,               f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, ''])

    def __transformSell(self, transaction, s, b, f):
        TradeStrategy.__log.debug("%s - Sell; %s, %s", transaction.dateTime,transaction.mergentId, s)
        description = 'Verkauf; {0}'.format(transaction.sell.unit)
        # crypto                       description, debit,                   credit,                  amount,   currency, exchangeRate,                baseCurrencyAmount,     shares
        yield self._book(transaction, [description, self._accounts.transfer, s.account,               s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount,  ''])
        # fiat
        yield self._book(transaction, [description, b.account,               self._accounts.transfer, b.amount, b.unit,   b.baseCurrency.exchangeRate, b.baseCurrency.amount,  ''])
        # fee
        yield self._book(transaction, [description, self._accounts.fees,     self._accounts.transfer, f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount , ''])
