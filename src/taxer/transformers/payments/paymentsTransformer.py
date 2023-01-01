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
        if transaction.id in self.__config:
            note = self.__config.get(transaction.id)
            return Payment(transaction, note)
        if  transaction.address in self.__config:
            note = self.__config.get(transaction.address)
            return Payment(transaction, note)
        return transaction
        
