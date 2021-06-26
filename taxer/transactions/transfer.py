from .transaction import Transaction


class Transfer(Transaction):
    def __init__(self, mergentId, dateTime, id, amount):
        super().__init__(mergentId, dateTime, id)
        self.__amount = amount

    @property
    def amount(self):
        return self.__amount

    def __str__(self):
        sup = super().__str__().replace('{', '').replace('}', '')
        return "{{{}, amount='{}'}}".format(sup, self.__amount)
