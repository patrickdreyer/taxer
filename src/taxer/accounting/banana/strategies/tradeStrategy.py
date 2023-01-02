import logging

from ....transactions.buyTrade import BuyTrade
from ....transactions.sellTrade import SellTrade
from ....transactions.trade import Trade
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class TradeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return issubclass(type(transaction), Trade)

    def transform(self, transaction):
        sell = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.sell, transaction)
        buy = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.buy, transaction)
        fee = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        if isinstance(transaction, BuyTrade):
            yield from self.__transformBuy(transaction, sell, buy, fee)
        elif isinstance(transaction, SellTrade):
            yield from self.__transformSell(transaction, sell, buy, fee)

    def __transformBuy(self, transaction, s, b, f):
        TradeStrategy.__log.debug("%s - Buy; %s, %s", transaction.dateTime, transaction.mergentId, b)
        description = 'Kauf; {0}'.format(transaction.buy.unit)
        # fiat                                            description, debit,                    credit,                   amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.transfer, s.account,                s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount, '',     s.costCenter.minus()])
        # crypto
        yield BananaStrategy._createBooking(transaction, [description, b.account,                self.__accounts.transfer, b.amount, b.unit,   b.baseCurrency.exchangeRate, b.baseCurrency.amount, '',     b.costCenter])
        # fee
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.fees,     s.account,                f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])

    def __transformSell(self, transaction, s, b, f):
        TradeStrategy.__log.debug("%s - Sell; %s, %s", transaction.dateTime,transaction.mergentId, s)
        description = 'Verkauf; {0}'.format(transaction.sell.unit)
        # crypto                                          description, debit,                    credit,                   amount,   currency, exchangeRate,                baseCurrencyAmount,     shares, costCenter1
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.transfer, s.account,                s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount,  '',     s.costCenter.minus()])
        # fiat
        yield BananaStrategy._createBooking(transaction, [description, b.account,                self.__accounts.transfer, b.amount, b.unit,   b.baseCurrency.exchangeRate, b.baseCurrency.amount,  '',     b.costCenter])
        # fee
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.fees,     self.__accounts.transfer, f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount , '',     ''])
