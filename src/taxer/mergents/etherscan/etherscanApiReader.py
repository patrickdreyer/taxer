from datetime import datetime
from pytz import utc

from .ether import Ether
from ..reader import Reader
from ...transactions.cancelFee import CancelFee
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.withdrawTransfer import WithdrawTransfer


class EtherscanApiReader(Reader):
    def __init__(self, config, etherscanApi, contracts):
        config['accounts'] = {k.lower():v for k,v in config['accounts'].items()}
        self.__config = config
        self.__etherscanApi = etherscanApi
        self.__contracts = {c.address:c for c in contracts}

    def read(self, year):
        for address,id in self.__config['accounts'].items():
            erc20Transactions = list(self.__etherscanApi.getErc20Transactions(address))
            transactions = self.__etherscanApi.getNormalTransactions(address)
            transactions = (self.__transformTransaction(t) for t in iter(transactions))
            transactions = (t for t in transactions if t['isError'] == '0')
            for transaction in transactions:
                contract = self.__getContractByTransaction(transaction)
                if contract != None:
                    erc20Transaction = EtherscanApiReader.__getErc20Transaction(erc20Transactions, transaction['hash'])
                    yield from contract.processTransaction(address, id, year, transaction, erc20Transaction)
                elif transaction['from'] == address and transaction['to'] == address:
                    if transaction['dateTime'].year == year:
                        yield CancelFee(id, transaction['dateTime'], transaction['hash'], Ether.fee(transaction))
                elif transaction['from'] == address:
                    if transaction['dateTime'].year == year:
                        yield WithdrawTransfer(id, transaction['dateTime'], transaction['hash'], Ether.amount(transaction), Ether.fee(transaction), transaction['to'])
                elif transaction['to'] == address:
                    if transaction['dateTime'].year == year:
                        yield DepositTransfer(id, transaction['dateTime'], transaction['hash'], Ether.amount(transaction), Ether.zero(), transaction['from'])

    def __transformTransaction(self, transaction):
        transaction['dateTime'] = utc.localize(datetime.fromtimestamp(int(transaction['timeStamp'])))
        return transaction

    def __getContractByTransaction(self, transaction):
        token = self.__getContractByAddress(transaction['from'])
        if token: return token
        token = self.__getContractByAddress(transaction['to'])
        if token: return token
        return None

    def __getContractByAddress(self, address):
        return self.__contracts[address] if address in self.__contracts else None

    @staticmethod
    def __getErc20Transaction(transactions, hash):
        transaction = [t for t in transactions if t['hash'] == hash]
        return transaction[0] if len(transaction) > 0 else None
