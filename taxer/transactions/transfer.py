from .transaction import Transaction


class Transfer(Transaction):
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

    def __str__(self):
        sup = super().__str__().replace('{', '').replace('}', '')
        return "{{{}, amount='{}', fee='{}'}}".format(sup, self.__amount, self.__fee)
