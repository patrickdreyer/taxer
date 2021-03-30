from .transaction import Transaction


class Trade(Transaction):
    __mergentId = None
    __dateTime = None
    __id = None
    __cryptoUnit = None
    __cryptoAmount = None
    __fiatUnit = None
    __fiatAmount = None
    __feeAmount = None

    def __init__(self, mergentId, dateTime, id, cryptoUnit, cryptoAmount, fiatUnit, fiatAmount, feeAmount):
        self.__mergentId = mergentId
        self.__dateTime = dateTime
        self.__id = id
        self.__cryptoUnit = cryptoUnit
        self.__cryptoAmount = cryptoAmount
        self.__fiatUnit = fiatUnit
        self.__fiatAmount = fiatAmount
        self.__feeAmount = feeAmount

    @property
    def mergentId(self):
        return self.__mergentId

    @property
    def dateTime(self):
        return self.__dateTime

    @property
    def id(self):
        return self.__id

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
