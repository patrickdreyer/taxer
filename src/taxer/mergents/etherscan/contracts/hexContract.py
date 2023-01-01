from datetime import datetime
from decimal import Decimal

from .contract import Contract
from ..ether import Ether
from ....transactions.currency import Currency
from ....transactions.enterLobby import EnterLobby
from ....transactions.endStake import EndStake
from ....transactions.exitLobby import ExitLobby
from ....transactions.payment import Payment
from ....transactions.startStake import StartStake


class HexContract(Contract):
    __id = 'HEX'
    __address = '0x2b591e99afE9f32eAA6214f7B7629768c40Eeb39'
    __firstLobbyDate = datetime(2019, 12, 3).date()
    __stakeStartTopic = '0x14872dc760f33532684e68e1b6d5fd3f71ba7b07dee76bdb2b084f28b74233ef'
    __divisor = 100000000

    __lobby = {}
    __stakes = {}

    @property
    def address(self): return HexContract.__address

    @property
    def web3Contract(self): return self.__web3Contract

    @property
    def functions(self): return self.__web3Contract.functions

    def __init__(self, contracts, etherscanApi):
        self.__etherscanApi = etherscanApi
        self.__web3Contract = etherscanApi.getContract(HexContract.__address)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        (name, args) = Ether.decodeContractInput(self.__web3Contract, transaction['input'])

        if name == 'xflobbyenter':
            day = (transaction['dateTime'].date() - HexContract.__firstLobbyDate).days
            self.__lobby[day] = transaction
            if transaction['dateTime'].year == year:
                yield EnterLobby(id, transaction['dateTime'], transaction['hash'], Ether.amountFromTransaction(transaction), Ether.feeFromTransaction(transaction), HexContract.__id)

        elif name == 'xflobbyexit':
            if transaction['dateTime'].year == year:
                day = args['enterDay']
                lobbyEnterTransaction = self.__lobby[day]
                yield ExitLobby(id, transaction['dateTime'], transaction['hash'], Ether.amountFromTransaction(lobbyEnterTransaction), HexContract.__amount(erc20Transaction), Ether.feeFromTransaction(transaction))

        elif name == 'stakestart':
            logs = self.__etherscanApi.getLogs(transaction['blockNumber'], transaction['to'], HexContract.__stakeStartTopic, transaction['from'])
            logs = [l for l in logs if l['transactionHash'] == transaction['hash']]
            stakeId = int(logs[0]['topics'][2], 16)
            self.__stakes[stakeId] = {
                'amount'   : HexContract.__amount(erc20Transaction),
                'shares'   : args['newStakedHearts'],
                'days'     : args['newStakedDays'],
                'startDate': transaction['dateTime'].date()
            }
            if transaction['dateTime'].year == year:
                yield StartStake(id, transaction['dateTime'], transaction['hash'], HexContract.__amount(erc20Transaction), Ether.feeFromTransaction(transaction))

        elif name == 'stakeend':
            if transaction['dateTime'].year == year:
                stakeId = args['stakeIdParam']
                if not stakeId in self.__stakes:
                    raise Exception("Stake end without matching Erc20 transaction; transactionHash='{}'".format(transaction['hash']))

                tokenAmountStaked = self.__stakes[stakeId]['amount']
                tokenAmountUnstaked = HexContract.__amount(erc20Transaction)
                tokenInterest = tokenAmountUnstaked - tokenAmountStaked
                yield EndStake(id, transaction['dateTime'], transaction['hash'], tokenAmountStaked, tokenInterest, tokenAmountUnstaked, Ether.feeFromTransaction(transaction))

        elif name == 'approve':
            if transaction['dateTime'].year == year:
                publicNameTag = self.__etherscanApi.getPublicNameTagByAddress(args['spender'])
                yield Payment(id, transaction['dateTime'], transaction['hash'], Ether.zero(), Ether.feeFromTransaction(transaction), publicNameTag)

        elif name == 'transfer':
            if transaction['dateTime'].year == year:
                publicNameTag = self.__etherscanApi.getPublicNameTagByAddress(args['recipient'])
                yield Payment(id, transaction['dateTime'], transaction['hash'], Ether.zero(), Ether.feeFromTransaction(transaction), publicNameTag)

        else:
            raise KeyError("Unknown token function; token='{}', functionName='{}'".format(HexContract.__id, name))

    @staticmethod
    def amount(value):
        return Currency(HexContract.__id, Decimal(value) / HexContract.__divisor)

    @staticmethod
    def __amount(transaction):
        return Currency(HexContract.__id, Decimal(transaction['value']) / Decimal('1' + '0'*int(transaction['tokenDecimal'])))
