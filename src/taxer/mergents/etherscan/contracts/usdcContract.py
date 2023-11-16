from decimal import Decimal

from .contract import Contract
from ..ether import Ether
from ....transactions.currency import Currency
from ....transactions.depositTransfer import DepositTransfer
from ....transactions.withdrawTransfer import WithdrawTransfer


class UsdcContract(Contract):
    __id = 'USDC'
    __divisor = 1000000

    def __init__(self, contracts, accounts:list[str], etherscanApi):
        super().__init__('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', None, accounts)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        if transaction['dateTime'].year != year:
            return

        name = transaction['functionName']

        if name.startswith('transfer'):
            if erc20Transaction['from'] == address:
                yield WithdrawTransfer(id, transaction['dateTime'], transaction['hash'], self.amount(erc20Transaction['value']), Ether.feeFromTransaction(transaction), address)
            elif erc20Transaction['to'] == address:
                yield DepositTransfer(id, transaction['dateTime'], transaction['hash'], self.amount(erc20Transaction['value']), Ether.zero(), address)

        else:
            raise KeyError("Unknown token function; token='{}', functionName='{}'".format(UsdcContract.__id, name))

    def amount(self, value) -> Currency:
        return Currency(UsdcContract.__id, Decimal(value) / UsdcContract.__divisor)
