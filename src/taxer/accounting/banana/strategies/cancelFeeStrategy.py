import logging

from ....transactions.cancelFee import CancelFee
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class CancelFeeStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return isinstance(transaction, CancelFee)

    def transform(self, transaction):
        CancelFeeStrategy.__log.debug("%s - Cancel fee; %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount)
        c = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        #                                    date,                          receipt,        description,     deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, 'Abbruchgebühr', self.__accounts.fees, c.account,  c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter.minus()])
