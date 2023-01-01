from .contract import Contract


class Axn2Contract(Contract):
    __address = '0x71f85b2e46976bd21302b64329868fd15eb0d127'

    @property
    def address(self): return Axn2Contract.__address

    def __init__(self, contracts, etherscanApi):
        pass

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        # we simply ignore any Axion transactions
        yield