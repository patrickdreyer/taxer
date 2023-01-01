from ..contract import Contract


class AxnContract(Contract):
    __address = '0x7d85e23014f84e6e21d5663acd8751bef3562352'

    @staticmethod
    def create():
        return AxnContract()

    @property
    def address(self): return AxnContract.__address

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        # we simply ignore any Axion transactions
        yield