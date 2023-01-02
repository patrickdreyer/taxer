import logging

from ....transactions.swap import Swap
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class SwapStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return isinstance(transaction, Swap)

    def transform(self, transaction):
        description = f"Swap {transaction.sourceAmount.unit} -> {transaction.destinationAmount.unit}"
        sf = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.sourceAmount, transaction)
        st = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.destinationAmount, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        SwapStrategy.__log.debug("%s - Swap; %s->%s", transaction.dateTime, transaction.sourceAmount, transaction.destinationAmount)
        # swapTo,                                         description, deposit,              withdrawal, amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares, costCenter1
        yield BananaStrategy._createBooking(transaction, [description, st.account,           '',         st.amount, st.unit,  st.baseCurrency.exchangeRate, st.baseCurrency.amount, '',     st.costCenter])
        # swapFrom
        yield BananaStrategy._createBooking(transaction, [description, '',                   sf.account, sf.amount, sf.unit,  sf.baseCurrency.exchangeRate, sf.baseCurrency.amount, '',     sf.costCenter.minus()])
        # fee
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.fees, f.account,  f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  '',     f.costCenter.minus()])
