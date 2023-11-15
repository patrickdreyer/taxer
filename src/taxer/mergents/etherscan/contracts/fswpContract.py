from .contract import Contract


class FswpContract(Contract):
    def __init__(self, contracts, accounts:list[str], etherscanApi):
        super().__init__('0x25bE894d8b04ea2a3d916FeC9B32ec0f38d08aA9', None, accounts)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        # we simply ignore any Axion transactions
        yield