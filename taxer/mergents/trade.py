from .transaction import Transaction


class Trade(Transaction):
    __mergentId = None
    __date = None
    __id = None
    __debitUnit = None
    __debitAmount = None
    __creditUnit = None
    __creditAmount = None
    __fee = None

    def __init__(self, mergentId, date, id, debitUnit, debitAmount, creditUnit, creditAmount, fee):
        self.__mergentId = mergentId
        self.__date = date
        self.__id = id
        self.__debitUnit = debitUnit
        self.__debitAmount = debitAmount
        self.__creditUnit = creditUnit
        self.__creditAmount = creditAmount
        self.__fee = fee

    @property
    def mergentId(self):
        return self.__mergentId

    @property
    def date(self):
        return self.__date

    @property
    def id(self):
        return self.__id

    @property
    def debitUnit(self):
        return self.__debitUnit

    @property
    def debitAmount(self):
        return self.__debitAmount

    @property
    def creditUnit(self):
        return self.__creditUnit

    @property
    def creditAmount(self):
        return self.__creditAmount

    @property
    def fee(self):
        return self.__fee
