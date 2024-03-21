from datetime import datetime
from decimal import Decimal

from .contract import Contract
from ..pulse import Pulse
from ....transactions.currency import Currency
from ....transactions.depositTransfer import DepositTransfer
from ....transactions.enterLobby import EnterLobby
from ....transactions.endStake import EndStake
from ....transactions.exitLobby import ExitLobby
from ....transactions.payment import Payment
from ....transactions.startStake import StartStake
from ....transactions.withdrawTransfer import WithdrawTransfer


class HexContract(Contract):
    __id = 'HEX'
    __firstLobbyDate = datetime(2019, 12, 3).date()
    __stakeStartTopic = '0x14872dc760f33532684e68e1b6d5fd3f71ba7b07dee76bdb2b084f28b74233ef'
    __divisor = 100000000

    __lobby = {}
    __stakes = {}

    def __init__(self, accounts:list[str], api):
        super().__init__('0x2b591e99afE9f32eAA6214f7B7629768c40Eeb39', None, accounts, api)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        (name, args) = Pulse.decodeContractInput(transaction['decoded_input'])

        if name == 'xflobbyenter':
            day = (transaction['dateTime'].date() - HexContract.__firstLobbyDate).days
            self.__lobby[day] = transaction
            if transaction['dateTime'].year == year:
                yield EnterLobby(id, transaction['dateTime'], transaction['hash'], Pulse.amountFromTransaction(transaction), Pulse.feeFromTransaction(transaction), HexContract.__id)

        elif name == 'xflobbyexit':
            if transaction['dateTime'].year == year:
                day = args['enterDay']
                lobbyEnterTransaction = self.__lobby[day]
                yield ExitLobby(id, transaction['dateTime'], transaction['hash'], Pulse.amountFromTransaction(lobbyEnterTransaction), HexContract.__amount(erc20Transaction), Pulse.feeFromTransaction(transaction))

        elif name == 'stakestart':
            logs = self.api.getLogs(transaction['hash'], topic0 = HexContract.__stakeStartTopic, topic1 = Pulse.toTopic(transaction['from']['hash']))
            stakeId = int(logs[0]['topics'][2], 16)
            self.__stakes[stakeId] = {
                'amount'   : HexContract.__amount(erc20Transaction),
                'shares'   : args['newStakedHearts'],
                'days'     : args['newStakedDays'],
                'startDate': transaction['dateTime'].date()
            }
            if transaction['dateTime'].year == year:
                yield StartStake(id, transaction['dateTime'], transaction['hash'], stakeId, HexContract.__amount(erc20Transaction), Pulse.feeFromTransaction(transaction))

        elif name == 'stakeend':
            if transaction['dateTime'].year == year:
                stakeId = args['stakeIdParam']
                if not stakeId in self.__stakes:
                    raise Exception(f"Stake end without matching Erc20 transaction; transactionHash='{transaction['hash']}'")

                tokenAmountStaked = self.__stakes[stakeId]['amount']
                tokenAmountUnstaked = HexContract.__amount(erc20Transaction)
                tokenInterest = tokenAmountUnstaked - tokenAmountStaked
                yield EndStake(id, transaction['dateTime'], transaction['hash'], stakeId, tokenAmountStaked, tokenInterest, tokenAmountUnstaked, Pulse.feeFromTransaction(transaction))

        elif name == 'approve':
            if transaction['dateTime'].year == year:
                publicNameTag = self.__contracts.getPublicNameTagByAddress(args['spender'])
                yield Payment(id, transaction['dateTime'], transaction['hash'], Pulse.zero(), Pulse.feeFromTransaction(transaction), publicNameTag)

        elif name == 'transfer':
            if transaction['dateTime'].year == year:
                recipientId  = self.getMergendIdByAddress(args['recipient'])
                amount = self.amount(args['amount'])
                if transaction['to']['hash'].lower() == self.address.lower():
                    yield WithdrawTransfer(id, transaction['dateTime'], transaction['hash'], amount, Pulse.feeFromTransaction(transaction), transaction['from']['hash'])
                    if recipientId != None:
                        yield DepositTransfer(recipientId, transaction['dateTime'], transaction['hash'], amount, Pulse.zero(), args['recipient'])
                elif transaction['from']['hash'].lower() == self.address.lower():
                    if recipientId != None:
                        yield WithdrawTransfer(recipientId, transaction['dateTime'], transaction['hash'], amount, Pulse.feeFromTransaction(transaction), args['recipient'])
                    yield DepositTransfer(id, transaction['dateTime'], transaction['hash'], amount, Pulse.zero(), transaction['to']['hash'])

        else:
            raise KeyError(f"Unknown token function; token='{HexContract.__id}', functionName='{name}'")

    def amount(self, value) -> Currency:
        return Currency(HexContract.__id, Decimal(value) / HexContract.__divisor)

    @staticmethod
    def __amount(transaction):
        return Currency(HexContract.__id, Decimal(transaction['total']['value']) / Decimal('1' + '0'*int(transaction['total']['decimals'])))
