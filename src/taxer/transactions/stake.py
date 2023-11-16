from .transaction import Transaction


class Stake(Transaction):
    def __init__(self, mergentId, dateTime, id, stakeId, amount, fee):
        super().__init__(mergentId, dateTime, id)
        self.__stakeId = stakeId
        self.__amount = amount
        self.__fee = fee

    @property
    def stakeId(self):
        return self.__stakeId


    @property
    def amount(self):
        return self.__amount

    @property
    def fee(self):
        return self.__fee
