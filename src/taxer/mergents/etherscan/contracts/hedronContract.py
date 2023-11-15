from decimal import Decimal

from .contract import Contract
from ..ether import Ether
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
            if transaction['from'] == address:
                yield WithdrawTransfer(id, transaction['dateTime'], transaction['hash'], HedronContract.__amount(args['amount']), Ether.feeFromTransaction(transaction), address)
            elif transaction['to'] == address:
                yield DepositTransfer(id, transaction['dateTime'], transaction['hash'], HedronContract.__amount(args['amount']), Ether.zero(), address)

        elif name == 'claimnative':
            yield Fee(id, transaction['dateTime'], transaction['hash'], Ether.feeFromTransaction(transaction))
            # Process fee only as claimed tokens are given with the first minting, see mintnative

        elif name == 'mintnative':
            yield Mint(id, transaction['dateTime'], transaction['hash'], HedronContract.__amountFromTransaction(erc20Transaction), Ether.feeFromTransaction(transaction))

        else:
            raise KeyError("Unknown token function; token='{}', functionName='{}'".format(HedronContract.__id, name))

    @staticmethod
    def __amount(value):
        return Currency(HedronContract.__id, Decimal(value) / HedronContract.__divisor)

    @staticmethod
    def __amountFromTransaction(transaction):
        return Currency(HedronContract.__id, Decimal(transaction['value']) / Decimal('1' + '0'*int(transaction['tokenDecimal'])))
