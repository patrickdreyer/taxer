from decimal import Decimal

from ..contract import Contract
from ..ether import Ether
from ....transactions.currency import Currency
from ....transactions.depositTransfer import DepositTransfer
from ....transactions.mint import Mint
from ....transactions.withdrawTransfer import WithdrawTransfer


# https://hedron.pro/#/guide
class HedronContract(Contract):
    __id = 'HDRN'
    __address = '0x3819f64f282bf135d62168c1e513280daf905e06'

    @staticmethod
    def create(etherscanApi):
        contract = Ether.getContract(etherscanApi, HedronContract.__address)
        return HedronContract(contract)

    @property
    def address(self): return HedronContract.__address

    def __init__(self, contract):
        self.__contract = contract

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        if transaction['dateTime'].year != year:
            return

        (name, args) = Ether.decodeContractInput(self.__contract, transaction['input'])

        if name == 'transfer':
            if transaction['from'] == address:
                yield WithdrawTransfer(id, transaction['dateTime'], transaction['hash'], HedronContract.__amount(args['amount']), Ether.fee(transaction))
            elif transaction['to'] == address:
                yield DepositTransfer(id, transaction['dateTime'], transaction['hash'], HedronContract.__amount(args['amount']), Ether.zero())

        elif name == 'claimnative':
            # see mintNative as claimed tokens are given with the first minting
            return

        elif name == 'mintnative':
            yield Mint(id, transaction['dateTime'], transaction['hash'], HedronContract.__amountFromTransaction(erc20Transaction), Ether.fee(transaction))

        else:
            raise KeyError("Unknown token function; token='{}', functionName='{}'".format(HedronContract.__id, name))

    @staticmethod
    def __amount(amount):
        return Currency(HedronContract.__id, amount)

    @staticmethod
    def __amountFromTransaction(transaction):
        return Currency(HedronContract.__id, Decimal(transaction['value']) / Decimal('1' + '0'*int(transaction['tokenDecimal'])))
