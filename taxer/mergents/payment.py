from .transaction import Transaction
from .withdrawTransfer import WithdrawTransfer


class Payment(Transaction):
    def __init__(self, withdrawTransfer, note):
        super().__init__(withdrawTransfer.mergentId, withdrawTransfer.dateTime, withdrawTransfer.id, note)
        self.__unit = withdrawTransfer.unit
        self.__amount = withdrawTransfer.amount

    @property
    def unit(self):
        return self.__unit

    @property
    def amount(self):
        return self.__amount
