from .contract import Contract


class AxnContract(Contract):
    def __init__(self, contracts, etherscanApi):
        super().__init__('0x7D85e23014F84E6E21d5663aCD8751bEF3562352', None)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        # we simply ignore any Axion transactions
        yield