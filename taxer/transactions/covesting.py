from .transaction import Transaction


class Covesting(Transaction):
    def __init__(self, mergentId, dateTime, id, trader, unit, entryFee, amount, exitFee):
        super().__init__(mergentId, dateTime, id)
        self.__trader = trader
        self.__unit = unit
        self.__entryFee = entryFee
        self.__amount = amount
        self.__exitFee = exitFee

    @property
    def trader(self):
        return self.__trader

    @property
    def unit(self):
        return self.__unit

    @property
    def entryFee(self):
        return self.__entryFee

    @property
    def amount(self):
        return self.__amount

    @property
    def exitFee(self):
        return self.__exitFee
