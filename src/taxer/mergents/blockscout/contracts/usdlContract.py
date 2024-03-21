from decimal import Decimal

from .contract import Contract
from ..pulse import Pulse
from ....transactions.currency import Currency
from ....transactions.depositTransfer import DepositTransfer
from ....transactions.withdrawTransfer import WithdrawTransfer


class UsdlContract(Contract):
    __id = 'USDL'
    __divisor = 1000000000000000000

    def __init__(self, accounts:list[str], api):
        super().__init__('0x0dEEd1486bc52aA0d3E6f8849cEC5adD6598A162', None, accounts, api)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        if transaction['dateTime'].year != year:
            return

        (name, args) = Pulse.decodeContractInput(transaction['decoded_input'])

        if name == 'transfer':
            if erc20Transaction['from'] == address:
                yield WithdrawTransfer(id, transaction['dateTime'], transaction['hash'], self.amount(erc20Transaction['value']), Pulse.feeFromTransaction(transaction), address)
            elif erc20Transaction['to'] == address:
                yield DepositTransfer(id, transaction['dateTime'], transaction['hash'], self.amount(erc20Transaction['value']), Pulse.zero(), address)

        else:
            raise KeyError(f"Unknown token function; token='{UsdlContract.__id}', functionName='{name}'")

    def amount(self, value) -> Currency:
        return Currency(UsdlContract.__id, Decimal(value) / UsdlContract.__divisor)
