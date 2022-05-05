from .transaction import Transaction


class Mint(Transaction):
    def __init__(self, mergentId, dateTime, id, amount, fee):
        super().__init__(mergentId, dateTime, id)
        self.__amount = amount
        self.__fee = fee

    @property
    def amount(self):
        return self.__amount

    @property
    def fee(self):
        return self.__fee
