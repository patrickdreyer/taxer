from ..token import Token


class Axn2Token(Token):
    __address = '0x71f85b2e46976bd21302b64329868fd15eb0d127'

    @staticmethod
    def create():
        return Axn2Token()

    @property
    def address(self): return Axn2Token.__address

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        # we simply ignore any Axion transactions
        yield