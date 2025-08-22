from .transaction import Transaction


class Trade(Transaction):
    def __init__(self, mergentId, dateTime, id, sell, buy, fee):
        super().__init__(mergentId, dateTime, id)
        self.__sell = sell
        self.__buy = buy
        self.__fee = fee

    @property
    def sell(self):
        return self.__sell

    @property
    def buy(self):
        return self.__buy

    @property
    def fee(self):
        return self.__fee
