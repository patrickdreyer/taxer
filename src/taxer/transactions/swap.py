from .transaction import Transaction


class Swap(Transaction):
    def __init__(self, mergentId, dateTime, id, sourceAmount, destinationAmount, fee, provider):
        super().__init__(mergentId, dateTime, id, provider)
        self.__sourceAmount = sourceAmount
        self.__destinationAmount = destinationAmount
        self.__fee = fee

    @property
    def sourceAmount(self):
        return self.__sourceAmount

    @property
    def destinationAmount(self):
        return self.__destinationAmount

    @property
    def fee(self):
        return self.__fee

    def __str__(self):
        sup = super().__str__().replace('{', '').replace('}', '')
        return f"{{{sup}, sourceAmount='{self.__sourceAmount}', destinationAmount='{self.__destinationAmount}', fee='{self.__fee}'}}"
