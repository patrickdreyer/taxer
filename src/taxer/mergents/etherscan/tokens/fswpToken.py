from ..token import Token


class FswpToken(Token):
    __address = '0x25be894d8b04ea2a3d916fec9b32ec0f38d08aa9'

    @staticmethod
    def create():
        return FswpToken()

    @property
    def address(self): return FswpToken.__address

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        # we simply ignore any Axion transactions
        yield