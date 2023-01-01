from ..contract import Contract


class FswpContract(Contract):
    __address = '0x25be894d8b04ea2a3d916fec9b32ec0f38d08aa9'

    @property
    def address(self): return FswpContract.__address

    def __init__(self, etherscanApi):
        pass

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        # we simply ignore any Axion transactions
        yield