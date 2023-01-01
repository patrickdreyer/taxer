from .transaction import Transaction


class Transfer(Transaction):
    def __init__(self, mergentId, dateTime, id, amount, fee, address, note=''):
        super().__init__(mergentId, dateTime, id, note)
        self.__amount = amount
        self.__fee = fee
        self.__address = address

    @property
    def amount(self):
        return self.__amount

    @property
    def fee(self):
        return self.__fee

    @property
    def address(self):
        return self.__address

    def __str__(self):
        sup = super().__str__().replace('{', '').replace('}', '')
        return "{{{}, amount='{}', fee='{}', address='{}'}}".format(sup, self.__amount, self.__fee, self.__address)
