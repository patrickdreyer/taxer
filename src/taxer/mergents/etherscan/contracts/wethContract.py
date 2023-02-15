from decimal import Decimal

from .contract import Contract
from ....transactions.currency import Currency


class WethContract(Contract):
    __id = 'WETH'
    __divisor = 1000000000000000000

    def __init__(self, contracts, etherscanApi):
        super().__init__('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', None)
        self.__contract = etherscanApi.getContract(self.address)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        raise NotImplementedError(f"Not implemented contact; id={WethContract.__id}")

    def amount(self, value):
        return Currency(WethContract.__id, Decimal(value) / WethContract.__divisor)
