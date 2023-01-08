import logging

from ....container import Container
from ....transactions.buyTrade import BuyTrade
from ....transactions.sellTrade import SellTrade
from ....transactions.trade import Trade
from ..bananaStrategy import BananaStrategy


class TradeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, container:Container):
        super(TradeStrategy, self).__init__(container)
        self.__accounts = container['banana']['accounts']

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
        # fiat                         description, debit,                    credit,                   amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield self._book(transaction, [description, self.__accounts.transfer, s.account,                s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount, '',     s.costCenter.minus()])
        # crypto
        yield self._book(transaction, [description, b.account,                self.__accounts.transfer, b.amount, b.unit,   b.baseCurrency.exchangeRate, b.baseCurrency.amount, '',     b.costCenter])
        # fee
        yield self._book(transaction, [description, self.__accounts.fees,     s.account,                f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])

    def __transformSell(self, transaction, s, b, f):
        TradeStrategy.__log.debug("%s - Sell; %s, %s", transaction.dateTime,transaction.mergentId, s)
        description = 'Verkauf; {0}'.format(transaction.sell.unit)
        # crypto                       description, debit,                    credit,                   amount,   currency, exchangeRate,                baseCurrencyAmount,     shares, costCenter1
        yield self._book(transaction, [description, self.__accounts.transfer, s.account,                s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount,  '',     s.costCenter.minus()])
        # fiat
        yield self._book(transaction, [description, b.account,                self.__accounts.transfer, b.amount, b.unit,   b.baseCurrency.exchangeRate, b.baseCurrency.amount,  '',     b.costCenter])
        # fee
        yield self._book(transaction, [description, self.__accounts.fees,     self.__accounts.transfer, f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount , '',     ''])
