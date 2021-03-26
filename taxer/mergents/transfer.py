from .transaction import Transaction


class Transfer(Transaction):
    __id = None
    def __init__(self, id, unit, time, amount):
        super(Transfer, self).__init__(unit, time, amount)
        self.__id = id
