from decimal import Decimal

from .hexToken import HexToken
from ..ether import Ether
from ..token import Token
from ....transactions.currency import Currency
from ....transactions.mint import Mint


# https://hedron.pro/#/guide
class HedronToken(Token):
    __id = 'HDRN'
    __address = '0x3819f64f282bf135d62168c1e513280daf905e06'

    @staticmethod
    def create(etherscanApi):
        contract = Ether.getContract(etherscanApi, HedronToken.__address)
        return HedronToken(etherscanApi, contract)

    @property
    def address(self): return HedronToken.__address

    def __init__(self, etherscanApi, contract):
        self.__contract = contract

    def processTransaction(self, id, year, transaction, erc20Transaction):
        (name, args) = Ether.getFunction(self.__contract, transaction['input'])

        if name == 'claimnative':
            # see mintNative as claimed tokens are given with the first minting
            return

        elif name == 'mintnative':
            if transaction['dateTime'].year == year:
                yield Mint(id, transaction['dateTime'], transaction['hash'], HedronToken.__amount(erc20Transaction), Ether.fee(transaction))

        else:
            raise KeyError("Unknown token function; token='{}', functionName='{}'".format(HedronToken.__id, name))

    @staticmethod
    def __amount(transaction):
        return Currency(HedronToken.__id, Decimal(transaction['value']) / Decimal('1' + '0'*int(transaction['tokenDecimal'])))
