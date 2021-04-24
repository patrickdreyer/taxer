from .lobby import Lobby


class ExitLobby(Lobby):
    def __init__(self, mergentId, dateTime, id, unitLobby, amountLobby, unit, amount, fee):
        super().__init__(mergentId, dateTime, id)
        self.__unitLobby = unitLobby
        self.__amountLobby = amountLobby
        self.__unit = unit
        self.__amount = amount
        self.__fee = fee

    @property
    def unitLobby(self):
        return self.__unitLobby

    @property
    def amountLobby(self):
        return self.__amountLobby

    @property
    def unit(self):
        return self.__unit

    @property
    def amount(self):
        return self.__amount

    @property
    def fee(self):
        return self.__fee
