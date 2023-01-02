import logging

from ....transactions.marginTrade import MarginTrade
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class MarginTradeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return isinstance(transaction, MarginTrade)

    def transform(self, transaction):
        # gain/loss
        a = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        # entry fee
        e = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.entryFee, transaction)
        # exit fee
        x = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.exitFee, transaction)
        #                                        date,                          receipt,        description,               deposit,                withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,   shares, costCenter1
        if e.amount > 0:
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, 'Margin Trade - Einstieg', self.__accounts.fees,   e.account,              e.amount, e.unit,   e.baseCurrency.exchangeRate, e.baseCurrency.amount, '',    e.costCenter.minus()])
        if a.amountRaw >= 0:
            MarginTradeStrategy.__log.debug("%s - Margin gain; %s, %s", transaction.dateTime, transaction.mergentId, a)
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, 'Margin Trade - Gewinn',   a.account,              self.__accounts.equity, a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, '',    a.costCenter])
        else:
            MarginTradeStrategy.__log.debug("%s - Margin loss; %s, %s", transaction.dateTime, transaction.mergentId, a)
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, 'Margin Trade - Verlust',  self.__accounts.equity, a.account,              a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, '',    a.costCenter.minus()])
        yield     (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, 'Margin Trade - Ausstieg', self.__accounts.fees,   a.account,              x.amount, a.unit,   x.baseCurrency.exchangeRate, x.baseCurrency.amount, '',    x.costCenter.minus()])
