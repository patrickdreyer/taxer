from decimal import Decimal

from .contract import Contract
from ....transactions.currency import Currency


class WethContract(Contract):
    __id = 'WETH'
    __address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    __divisor = 1000000000000000000

    @property
    def address(self): return WethContract.__address

    def __init__(self, contracts, etherscanApi):
        self.__contract = etherscanApi.getContract(WethContract.__address)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        raise NotImplementedError(f"Not implemented contact; id={WethContract.__id}")

    @staticmethod
    def amount(value):
        return Currency(WethContract.__id, Decimal(value) / WethContract.__divisor)
