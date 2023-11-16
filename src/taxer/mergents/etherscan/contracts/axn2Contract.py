from .contract import Contract
from ....transactions.currency import Currency


class Axn2Contract(Contract):
    def __init__(self, contracts, accounts:list[str], etherscanApi):
        super().__init__('0x71F85B2E46976bD21302B64329868fd15eb0D127', None, accounts)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        # we simply ignore any Axion transactions
        yield

    def processErc20Transfer(self, address, id, year, erc20Transaction):
        # we simply ignore any Axion transactions
        yield

    def amount(self, value) -> Currency:
        raise NotImplementedError('Axn2Contract.amount() not supported')
