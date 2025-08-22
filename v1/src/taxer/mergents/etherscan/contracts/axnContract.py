from .contract import Contract
from ....transactions.currency import Currency


class AxnContract(Contract):
    def __init__(self, contracts, accounts:list[str], etherscanApi):
        super().__init__('0x7D85e23014F84E6E21d5663aCD8751bEF3562352', None, accounts)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        # we simply ignore any Axion transactions
        yield

    def processErc20Transfer(self, address, id, year, erc20Transaction):
        # we simply ignore any Axion transactions
        yield

    def amount(self, value) -> Currency:
        raise NotImplementedError('AxnContract.amount() not supported')
