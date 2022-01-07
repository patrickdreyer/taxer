from .transaction import Transaction


class Lobby(Transaction):
    def __init__(self, mergentId, dateTime, id):
        super().__init__(mergentId, dateTime, id)
