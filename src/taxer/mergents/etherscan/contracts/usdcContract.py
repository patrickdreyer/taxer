from decimal import Decimal

from .contract import Contract
from ....transactions.currency import Currency


class UsdcContract(Contract):
    __id = 'USDC'
    __address = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
    __divisor = 1 # TODO

    @property
    def address(self): return UsdcContract.__address

    def __init__(self, contracts, etherscanApi):
        self.__contract = etherscanApi.getContract(UsdcContract.__address)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        raise NotImplementedError(f"Not implemented contact; id={UsdcContract.__id}")

    @staticmethod
    def amount(value):
        return Currency(UsdcContract.__id, Decimal(value) / UsdcContract.__divisor)
