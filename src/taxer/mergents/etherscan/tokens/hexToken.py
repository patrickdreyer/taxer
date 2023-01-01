from datetime import datetime
from decimal import Decimal

from ..ether import Ether
from ..token import Token
from ....transactions.currency import Currency
from ....transactions.enterLobby import EnterLobby
from ....transactions.endStake import EndStake
from ....transactions.exitLobby import ExitLobby
from ....transactions.payment import Payment
from ....transactions.startStake import StartStake


class HexToken(Token):
    __id = 'HEX'
    __address = '0x2b591e99afe9f32eaa6214f7b7629768c40eeb39'
    __firstLobbyDate = datetime(2019, 12, 3).date()
    __stakeStartTopic = '0x14872dc760f33532684e68e1b6d5fd3f71ba7b07dee76bdb2b084f28b74233ef'

    __lobby = {}
    __stakes = {}

    @staticmethod
    def create(etherscanApi):
        contract = Ether.getContract(etherscanApi, HexToken.__address)
        return HexToken(etherscanApi, contract)

    @property
    def address(self): return HexToken.__address

    def __init__(self, etherscanApi, contract):
        self.__etherscanApi = etherscanApi
        self.__contract = contract

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        (name, args) = Ether.decodeContractInput(self.__contract, transaction['input'])

        if name == 'xflobbyenter':
            day = (transaction['dateTime'].date() - HexToken.__firstLobbyDate).days
            self.__lobby[day] = transaction
            if transaction['dateTime'].year == year:
                yield EnterLobby(id, transaction['dateTime'], transaction['hash'], Ether.amount(transaction), Ether.fee(transaction), HexToken.__id)

        elif name == 'xflobbyexit':
            if transaction['dateTime'].year == year:
                day = args['enterDay']
                lobbyEnterTransaction = self.__lobby[day]
                yield ExitLobby(id, transaction['dateTime'], transaction['hash'], Ether.amount(lobbyEnterTransaction), HexToken.__amount(erc20Transaction), Ether.fee(transaction))

        elif name == 'stakestart':
            logs = self.__etherscanApi.getLogs(transaction['blockNumber'], transaction['to'], HexToken.__stakeStartTopic, transaction['from'])
            logs = [l for l in logs if l['transactionHash'] == transaction['hash']]
            stakeId = int(logs[0]['topics'][2], 16)
            self.__stakes[stakeId] = {
                'amount'   : HexToken.__amount(erc20Transaction),
                'shares'   : args['newStakedHearts'],
                'days'     : args['newStakedDays'],
                'startDate': transaction['dateTime'].date()
            }
            if transaction['dateTime'].year == year:
                yield StartStake(id, transaction['dateTime'], transaction['hash'], HexToken.__amount(erc20Transaction), Ether.fee(transaction))

        elif name == 'stakeend':
            if transaction['dateTime'].year == year:
                stakeId = args['stakeIdParam']
                if not stakeId in self.__stakes:
                    raise Exception("Stake end without matching Erc20 transaction; transactionHash='{}'".format(transaction['hash']))

                tokenAmountStaked = self.__stakes[stakeId]['amount']
                tokenAmountUnstaked = HexToken.__amount(erc20Transaction)
                tokenInterest = tokenAmountUnstaked - tokenAmountStaked
                yield EndStake(id, transaction['dateTime'], transaction['hash'], tokenAmountStaked, tokenInterest, tokenAmountUnstaked, Ether.fee(transaction))

        elif name == 'approve':
            if transaction['dateTime'].year == year:
                publicNameTag = self.__etherscanApi.getPublicNameTagByAddress(args['spender'])
                yield Payment(id, transaction['dateTime'], transaction['hash'], Ether.zero(), Ether.fee(transaction), publicNameTag)

        elif name == 'transfer':
            if transaction['dateTime'].year == year:
                publicNameTag = self.__etherscanApi.getPublicNameTagByAddress(args['recipient'])
                yield Payment(id, transaction['dateTime'], transaction['hash'], Ether.zero(), Ether.fee(transaction), publicNameTag)

        else:
            raise KeyError("Unknown token function; token='{}', functionName='{}'".format(HexToken.__id, name))

    @staticmethod
    def __amount(transaction):
        return Currency(HexToken.__id, Decimal(transaction['value']) / Decimal('1' + '0'*int(transaction['tokenDecimal'])))
