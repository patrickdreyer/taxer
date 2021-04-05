from .transaction import Transaction


class Trade(Transaction):
    def __init__(self, mergentId, dateTime, id, cryptoUnit, cryptoAmount, fiatUnit, fiatAmount, feeAmount):
        super().__init__(mergentId, dateTime, id)
        self.__cryptoUnit = cryptoUnit
        self.__cryptoAmount = cryptoAmount
        self.__fiatUnit = fiatUnit
        self.__fiatAmount = fiatAmount
        self.__feeAmount = feeAmount

    @property
    def cryptoUnit(self):
        return self.__cryptoUnit

    @property
    def cryptoAmount(self):
        return self.__cryptoAmount

    @property
    def fiatUnit(self):
        return self.__fiatUnit

    @property
    def fiatAmount(self):
        return self.__fiatAmount

    @property
    def feeAmount(self):
        return self.__feeAmount
