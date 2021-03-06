from .lobby import Lobby


class EnterLobby(Lobby):
    def __init__(self, mergentId, dateTime, id, amount, fee, lobby):
        super().__init__(mergentId, dateTime, id)
        self.__amount = amount
        self.__fee = fee
        self.__lobby = lobby

    @property
    def amount(self):
        return self.__amount

    @property
    def fee(self):
        return self.__fee

    @property
    def lobby(self):
        return self.__lobby
