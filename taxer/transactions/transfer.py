from .transaction import Transaction


class Transfer(Transaction):
    def __init__(self, mergentId, dateTime, id, unit, amount):
        super().__init__(mergentId, dateTime, id)
        self.__unit = unit
        self.__amount = amount

    @property
    def unit(self):
        return self.__unit

    @property
    def amount(self):
        return self.__amount

    def __str__(self):
        sup = super().__str__().replace('{', '').replace('}', '')
        return "{{{}, unit='{}', amount='{}'}}".format(sup, self.__unit, self.__amount)
