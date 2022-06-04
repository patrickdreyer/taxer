from ..token import Token


class AxnToken(Token):
    __address = '0x7d85e23014f84e6e21d5663acd8751bef3562352'

    @staticmethod
    def create():
        return AxnToken()

    @property
    def address(self): return AxnToken.__address

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        # we simply ignore any Axion transactions
        yield