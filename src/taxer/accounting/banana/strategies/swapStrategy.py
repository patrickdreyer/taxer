import logging

from ....transactions.swap import Swap
from ..bananaStrategy import BananaStrategy


class SwapStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return isinstance(transaction, Swap)

    def transform(self, transaction):
        description = f"Swap {transaction.sourceAmount.unit} -> {transaction.destinationAmount.unit}"
        sf = self._currency(transaction.sourceAmount, transaction)
        st = self._currency(transaction.destinationAmount, transaction)
        f = self._currency(transaction.fee, transaction)
        SwapStrategy.__log.debug("%s - Swap; %s->%s", transaction.dateTime, transaction.sourceAmount, transaction.destinationAmount)
        # swapTo,                      description, deposit,             withdrawal, amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares
        yield self._book(transaction, [description, st.account,          '',         st.amount, st.unit,  st.baseCurrency.exchangeRate, st.baseCurrency.amount, ''])
        # swapFrom
        yield self._book(transaction, [description, '',                  sf.account, sf.amount, sf.unit,  sf.baseCurrency.exchangeRate, sf.baseCurrency.amount, ''])
        # fee
        yield self._book(transaction, [description, self._accounts.fees, f.account,  f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  ''])
