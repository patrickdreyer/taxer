from decimal import Decimal


from .contract import Contract
from ..ether import Ether
from ....transactions.approval import Approval
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

    def __init__(self, contracts, accounts:list[str], etherscanApi):
        super().__init__('0x3819f64f282bf135d62168C1e513280dAF905e06', None, accounts)
        self.__web3Contract = etherscanApi.getContract(self.address)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        if transaction['dateTime'].year != year:
            return

        (name, args) = Ether.decodeContractInput(self.__web3Contract, transaction['input'])

        if name == 'transfer':
            recipientId  = self.getMergendIdByAddress(args['recipient'])
            amount = self.amount(args['amount'])
            if transaction['to'].lower() == self.address.lower():
                yield WithdrawTransfer(id, transaction['dateTime'], transaction['hash'], amount, Ether.feeFromTransaction(transaction), transaction['from'])
                if recipientId != None:
                    yield DepositTransfer(recipientId, transaction['dateTime'], transaction['hash'], amount, Ether.zero(), args['recipient'])
            elif transaction['from'].lower() == self.address.lower():
                if recipientId != None:
                    yield WithdrawTransfer(recipientId, transaction['dateTime'], transaction['hash'], amount, Ether.feeFromTransaction(transaction), args['recipient'])
                yield DepositTransfer(id, transaction['dateTime'], transaction['hash'], amount, Ether.zero(), transaction['to'])

        elif name == 'claimnative':
            yield Fee(id, transaction['dateTime'], transaction['hash'], Ether.feeFromTransaction(transaction))
            # Process fee only as claimed tokens are given with the first minting, see mintnative

        elif name == 'mintnative':
            yield Mint(id, transaction['dateTime'], transaction['hash'], HedronContract.__amountFromTransaction(erc20Transaction), Ether.feeFromTransaction(transaction))

        elif name == 'approve':
            yield from self.__processApprove(id, transaction, args)

        else:
            raise KeyError("Unknown token function; token='{}', functionName='{}'".format(HedronContract.__id, name))

    def __processApprove(self, id, transaction, args):
        yield Approval(id, transaction['dateTime'], transaction['hash'], Ether.feeFromTransaction(transaction))

    def amount(self, value) -> Currency:
        return Currency(HedronContract.__id, Decimal(value) / HedronContract.__divisor)

    @staticmethod
    def __amountFromTransaction(transaction):
        return Currency(HedronContract.__id, Decimal(transaction['value']) / Decimal('1' + '0'*int(transaction['tokenDecimal'])))
