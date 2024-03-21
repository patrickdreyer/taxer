from decimal import Decimal

from .contract import Contract
from ..pulse import Pulse
from ....transactions.currency import Currency
from ....transactions.fee import Fee
from ....transactions.depositTransfer import DepositTransfer
from ....transactions.mint import Mint
from ....transactions.withdrawTransfer import WithdrawTransfer


# https://hedron.pro/#/guide
class HedronContract(Contract):
    __id = 'HDRN'
    __divisor = 1000000000

    @property
    def web3Contract(self): return self.__web3Contract

    def __init__(self, accounts:list[str], api):
        super().__init__('0x3819f64f282bf135d62168C1e513280dAF905e06', None, accounts, api)
        self.__web3Contract = api.getContract(self.address)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        if transaction['dateTime'].year != year:
            return

        raise NotImplementedError('HedronContract')
        (name, args) = Pulse.decodeContractInput(self.__web3Contract, transaction['input'])

        if name == 'transfer':
            recipientId  = self.getMergendIdByAddress(args['recipient'])
            amount = self.amount(args['amount'])
            if transaction['to'].lower() == self.address.lower():
                yield WithdrawTransfer(id, transaction['dateTime'], transaction['hash'], amount, Pulse.feeFromTransaction(transaction), transaction['from']['hash'])
                if recipientId != None:
                    yield DepositTransfer(recipientId, transaction['dateTime'], transaction['hash'], amount, Pulse.zero(), args['recipient'])
            elif transaction['from'].lower() == self.address.lower():
                if recipientId != None:
                    yield WithdrawTransfer(recipientId, transaction['dateTime'], transaction['hash'], amount, Pulse.feeFromTransaction(transaction), args['recipient'])
                yield DepositTransfer(id, transaction['dateTime'], transaction['hash'], amount, Pulse.zero(), transaction['to']['hash'])

        elif name == 'claimnative':
            yield Fee(id, transaction['dateTime'], transaction['hash'], Pulse.feeFromTransaction(transaction))
            # Process fee only as claimed tokens are given with the first minting, see mintnative

        elif name == 'mintnative':
            yield Mint(id, transaction['dateTime'], transaction['hash'], HedronContract.__amountFromTransaction(erc20Transaction), Pulse.feeFromTransaction(transaction))

        else:
            raise KeyError(f"Unknown token function; token='{HedronContract.__id}', functionName='{name}'")

    def amount(self, value) -> Currency:
        return Currency(HedronContract.__id, Decimal(value) / HedronContract.__divisor)

    @staticmethod
    def __amountFromTransaction(transaction):
        return Currency(HedronContract.__id, Decimal(transaction['value']) / Decimal('1' + '0'*int(transaction['tokenDecimal'])))
