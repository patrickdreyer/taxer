import logging

from ....transactions.reimbursement import Reimbursement
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class ReimbursementStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return isinstance(transaction, Reimbursement)

    def transform(self, transaction):
        ReimbursementStrategy.__log.debug("%s - Reimbursement; %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount)
        c = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        #                                    date,                          receipt,        description,      deposit,   withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, 'Rückerstattung', c.account, self.__accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])
