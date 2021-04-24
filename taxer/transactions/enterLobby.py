class EnterLobby():
    def __init__(self, mergentId, dateTime, id, unitAmount, amount, unitFee, fee):
        self.__mergentId = mergentId
        self.__dateTime = dateTime
        self.__id = id
        self.__unitAmount = unitAmount
        self.__amount = amount
        self.__unitFee = unitFee
        self.__fee = fee

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
