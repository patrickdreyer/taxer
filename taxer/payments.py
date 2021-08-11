from .transactions.payment import Payment
from .transactions.withdrawTransfer import WithdrawTransfer


class Payments:
    def __init__(self, entries):
        self.__entries = entries

    def transform(self, transactions):
        return map(self.__map, transactions)

    def __map(self, transaction):
        if not isinstance(transaction, WithdrawTransfer):
            return transaction
        if not transaction.id in self.__entries:
            return transaction
        return Payment(transaction, self.__entries[transaction.id])
