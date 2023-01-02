import logging

from ....transactions.payment import Payment
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class PaymentStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return isinstance(transaction, Payment)

    def transform(self, transaction):
        PaymentStrategy.__log.debug("%s - Payment; %s, %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount, transaction.note)
        description = f'Bezahlung; {transaction.note}'
        w = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        #                                        date,                          receipt,        description, deposit,                withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield     (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, self.__accounts.equity, w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     w.costCenter.minus(), transaction.note])
        if transaction.fee.amount > 0:
            f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], '',             description, self.__accounts.fees,   w.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])
