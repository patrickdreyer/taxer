from .transaction import Transaction


class Covesting(Transaction):
    def __init__(self, mergentId, dateTime, id, trader, amount, entryFee, exitFee):
        super().__init__(mergentId, dateTime, id)
        self.__trader = trader
        self.__amount = amount
        self.__entryFee = entryFee
        self.__exitFee = exitFee

    @property
    def trader(self):
        return self.__trader

    @property
    def amount(self):
        return self.__amount

    @property
    def entryFee(self):
        return self.__entryFee

    @property
    def exitFee(self):
        return self.__exitFee
