from datetime import datetime
import logging
from pytz import utc

from .pulse import Pulse
from ..reader import Reader
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.fee import Fee
from ...transactions.withdrawTransfer import WithdrawTransfer


class BlockscoutApiReader(Reader):
    def __init__(self, accounts:list[str], api, contracts):
        self.__log = logging.getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))
        self.__accounts = {k.lower():v for k,v in accounts.items()}
        self.__api = api
        self.__contracts = contracts

    def read(self, year):
        for address,id in self.__accounts.items():
            transactions = self.__api.getNormalTransactions(address)
            transactions = (self.__transformTransaction(t) for t in iter(transactions))
            for transaction in transactions:
                if transaction['isError']:
                    if transaction['dateTime'].year == year:
                        yield Fee(id, transaction['dateTime'], transaction['hash'], Pulse.feeFromTransaction(transaction))
                else:
                    contract = self.__getContractByTransaction(transaction)
                    if contract != None:
                        erc20Transaction = self.__api.getErc20Transaction(transaction['hash'])
                        yield from contract.processTransaction(address, id, year, transaction, erc20Transaction)
                    elif transaction['from']['hash'] == address and transaction['to']['hash'] == address:
                        if transaction['dateTime'].year == year:
                            yield Fee(id, transaction['dateTime'], transaction['hash'], Pulse.feeFromTransaction(transaction))
                    elif transaction['from']['hash'] == address:
                        if transaction['dateTime'].year == year:
                            yield WithdrawTransfer(id, transaction['dateTime'], transaction['hash'], Pulse.amountFromTransaction(transaction), Pulse.feeFromTransaction(transaction), transaction['to']['hash'])
                    elif transaction['to']['hash'] == address:
                        if transaction['dateTime'].year == year:
                            yield DepositTransfer(id, transaction['dateTime'], transaction['hash'], Pulse.amountFromTransaction(transaction), Pulse.zero(), transaction['from']['hash'])

    def __transformTransaction(self, transaction):
        transaction['dateTime'] = utc.localize(datetime.fromisoformat(transaction['timestamp'].replace('Z', '')))
        transaction['isError'] = transaction['status'] == 'error'
        return transaction

    def __getContractByTransaction(self, transaction):
        if not transaction['from']['is_contract'] and not transaction['to']['is_contract']:
            return None
        
        if transaction['from']['is_contract']:
            token = self.__contracts.getByAddress(transaction['from']['hash'])
        elif transaction['to']['is_contract']:
            token = self.__contracts.getByAddress(transaction['to']['hash'])
        if not token:
            self.__log.error("Unknown contract; transaction='%s'", transaction['hash'])
            return None
        return token
