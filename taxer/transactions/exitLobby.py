from .lobby import Lobby


class ExitLobby(Lobby):
    def __init__(self, mergentId, dateTime, id, lobby, amount, fee):
        super().__init__(mergentId, dateTime, id)
        self.__lobby = lobby
        self.__amount = amount
        self.__fee = fee

    @property
    def lobby(self):
        return self.__lobby

    @property
    def amount(self):
        return self.__amount

    @property
    def fee(self):
        return self.__fee
