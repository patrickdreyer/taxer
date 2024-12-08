from .transaction import Transaction


class Approval(Transaction):
    def __init__(self, mergentId, dateTime, id, amount):
        super().__init__(mergentId, dateTime, id)
        self.__amount = amount

    @property
    def amount(self):
        return self.__amount
