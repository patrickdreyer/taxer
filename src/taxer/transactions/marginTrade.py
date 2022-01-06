from .transaction import Transaction


class MarginTrade(Transaction):
    def __init__(self, mergentId, dateTime, id, amount, entryFee, exitFee):
        super().__init__(mergentId, dateTime, id)
        self.__amount = amount
        self.__entryFee = entryFee
        self.__exitFee = exitFee

    @property
    def amount(self):
        return self.__amount

    @property
    def entryFee(self):
        return self.__entryFee

    @property
    def exitFee(self):
        return self.__exitFee
