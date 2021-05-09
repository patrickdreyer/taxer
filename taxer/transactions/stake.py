from .transaction import Transaction


class Stake(Transaction):
    def __init__(self, mergentId, dateTime, id, unitAmount, amount, unitFee, fee):
        super().__init__(mergentId, dateTime, id)
        self.__unitAmount = unitAmount
        self.__amount = amount
        self.__unitFee = unitFee
        self.__fee = fee

    @property
    def unitAmount(self):
        return self.__unitAmount

    @property
    def amount(self):
        return self.__amount

    @property
    def unitFee(self):
        return self.__unitFee

    @property
    def fee(self):
        return self.__fee
