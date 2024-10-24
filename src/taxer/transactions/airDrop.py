from .transaction import Transaction


class AirDrop(Transaction):
    def __init__(self, mergentId, dateTime, id, amount, note=''):
        super().__init__(mergentId, dateTime, id, note)
        self.__amount = amount

    @property
    def amount(self):
        return self.__amount
