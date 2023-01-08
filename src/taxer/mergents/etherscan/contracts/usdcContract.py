from decimal import Decimal

from .contract import Contract
from ....transactions.currency import Currency


class UsdcContract(Contract):
    __id = 'USDC'
    __divisor = 1 # TODO

    def __init__(self, contracts, etherscanApi):
        super().__init__('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', None)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        if transaction['dateTime'].year != year:
            yield from []
            return
        raise NotImplementedError(f"Not implemented contact; id={UsdcContract.__id}")

    def amount(self, value):
        return Currency(UsdcContract.__id, Decimal(value) / UsdcContract.__divisor)
