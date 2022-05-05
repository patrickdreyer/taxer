from datetime import date
from datetime import datetime

from .hexToken import HexToken
from ..ether import Ether
from ..token import Token
from ....transactions.claim import Claim
from ....transactions.currency import Currency
from ....transactions.mint import Mint


# https://hedron.pro/#/guide
class HedronToken(Token):
    __address = '0x3819f64f282bf135d62168c1e513280daf905e06'
    __firstHedronDay = date(2022, 2, 26)
    __startingMultiplier = 10
    __sameMultiplierDays = 10

    id = 'HDRN'

    __minted = {}

    @staticmethod
    def create(etherscanApi, stakes):
        contract = Ether.getContract(etherscanApi, HedronToken.__address)
        return HedronToken(etherscanApi, contract, stakes)

    @property
    def address(self): return HedronToken.__address

    def __init__(self, etherscanApi, contract, stakes):
        self.__etherscanApi = etherscanApi
        self.__contract = contract
        self.__stakes = stakes[HexToken.id] if (HexToken.id in stakes) else {}

    def processTransaction(self, id, year, transaction, erc20Transaction):
        (name, args) = Ether.getFunction(self.__contract, transaction['input'])

        stakeId = args['stakeId'] if 'stakeId' in args else None
        if name == 'claimnative':
            if (not stakeId in self.__stakes):
                raise KeyError("Unknown HEX stake; stakeId={}".format(stakeId))

            bShares = self.__getBShares(self.__stakes[stakeId])
            day = HedronToken.__getHedronDay()
            multiplier = HedronToken.__startingMultiplier - day // HedronToken.__sameMultiplierDays
            amount = Currency(HedronToken.id, bShares * multiplier)
            if transaction['dateTime'].year == year:
                yield Claim(id, transaction['dateTime'], transaction['hash'], amount, Ether.fee(transaction))

        elif name == 'mintNative':
            if (not stakeId in self.__stakes):
                raise KeyError("Unknown HEX stake; stakeId={}".format(stakeId))

            daysServed = HexToken.getDaysServed(self.__stakes[stakeId])
            self.__minted[stakeId] = daysServed
            if transaction['dateTime'].year == year:
                yield Mint(id, transaction['dateTime'], transaction['hash'], HedronToken.__amount(erc20Transaction), Ether.fee(transaction))

        else:
            raise KeyError("Unknown token function; token='{}', functionName='{}'".format(HedronToken.id, name))

    @staticmethod
    def __getHedronDay():
        return (datetime.now().date() - HedronToken.__firstHedronDay).days

    def __getBShares(self, hexStake):
        return hexStake['shares'] / 1000000000
