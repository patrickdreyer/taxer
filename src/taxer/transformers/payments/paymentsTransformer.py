from ..transformer import Transformer
from ...transactions.payment import Payment
from ...transactions.withdrawTransfer import WithdrawTransfer


class PaymentsTransformer(Transformer):
    def __init__(self, config):
        self.__config = config

    def transform(self, transactions):
        return map(self.__map, transactions)

    def __map(self, transaction):
        if not isinstance(transaction, WithdrawTransfer):
            return transaction
        if not transaction.id in self.__config:
            return transaction
        return Payment(transaction, self.__config[transaction.id])
