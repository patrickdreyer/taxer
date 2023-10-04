from datetime import datetime
from pytz import utc

from .ether import Ether
from ..reader import Reader
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.fee import Fee
from ...transactions.withdrawTransfer import WithdrawTransfer


class EtherscanApiReader(Reader):
    def __init__(self, accounts:list[str], etherscanApi, contracts):
        self.__accounts = {k.lower():v for k,v in accounts.items()}
        self.__etherscanApi = etherscanApi
        self.__contracts = contracts

    def read(self, year):
        for address,id in self.__accounts.items():
            erc20Transactions = list(self.__etherscanApi.getErc20Transactions(address))
            transactions = self.__etherscanApi.getNormalTransactions(address)
            transactions = (self.__transformTransaction(t) for t in iter(transactions))
            for transaction in transactions:
                if transaction['dateTime'].year > year:
                    continue

                if transaction['isError']:
                    if transaction['dateTime'].year == year:
                        yield Fee(id, transaction['dateTime'], transaction['hash'], Ether.feeFromTransaction(transaction))
                else:
                    contract = self.__getContractByTransaction(transaction)
                    if contract != None:
                        erc20Transaction = EtherscanApiReader.__getErc20Transaction(erc20Transactions, transaction['hash'])
                        yield from contract.processTransaction(address, id, year, transaction, erc20Transaction)
                    elif transaction['from'] == address and transaction['to'] == address:
                        if transaction['dateTime'].year == year:
                            yield Fee(id, transaction['dateTime'], transaction['hash'], Ether.feeFromTransaction(transaction))
                    elif transaction['from'] == address:
                        if transaction['dateTime'].year == year:
                            yield WithdrawTransfer(id, transaction['dateTime'], transaction['hash'], Ether.amountFromTransaction(transaction), Ether.feeFromTransaction(transaction), transaction['to'])
                    elif transaction['to'] == address:
                        if transaction['dateTime'].year == year:
                            yield DepositTransfer(id, transaction['dateTime'], transaction['hash'], Ether.amountFromTransaction(transaction), Ether.zero(), transaction['from'])

    def __transformTransaction(self, transaction):
        transaction['dateTime'] = utc.localize(datetime.fromtimestamp(int(transaction['timeStamp'])))
        transaction['isError'] = transaction['isError'] != '0'
        return transaction

    def __getContractByTransaction(self, transaction):
        token = self.__contracts.getByAddress(transaction['from'])
        if token: return token
        token = self.__contracts.getByAddress(transaction['to'])
        if token: return token
        return None

    @staticmethod
    def __getErc20Transaction(transactions, hash):
        transaction = [t for t in transactions if t['hash'] == hash]
        return transaction[0] if len(transaction) > 0 else None
