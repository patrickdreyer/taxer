from .trade import Trade


class BuyTrade(Trade):
    def __init__(self, mergentId, dateTime, id, crypto, fiat, fee):
        super().__init__(mergentId, dateTime, id, fiat, crypto, fee)
