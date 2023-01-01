from datetime import datetime
from pytz import utc

from .ether import Ether
from ..reader import Reader
from ...transactions.cancelFee import CancelFee
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.withdrawTransfer import WithdrawTransfer


class EtherscanApiReader(Reader):
    def __init__(self, config, etherscanApi, tokens, closedSourceContracts):
        config['accounts'] = {k.lower():v for k,v in config['accounts'].items()}
        self.__config = config
        self.__etherscanApi = etherscanApi
        self.__tokens = {t.address:t for t in tokens}
        self.__closedSourceContracts = {c.address:c for c in closedSourceContracts}

    def read(self, year):
        for address,id in self.__config['accounts'].items():
            erc20Transactions = list(self.__etherscanApi.getErc20Transactions(address))
            transactions = self.__etherscanApi.getNormalTransactions(address)
            transactions = (self.__transformTransaction(t) for t in iter(transactions))
            transactions = (t for t in transactions if t['isError'] == '0')
            for transaction in transactions:
                if transaction['token'] != None:
                    erc20Transaction = EtherscanApiReader.__getErc20Transaction(erc20Transactions, transaction['hash'])
                    yield from transaction['token'].processTransaction(address, id, year, transaction, erc20Transaction)
                elif transaction['dateTime'].year == year:
                    if transaction['from'] == address and transaction['to'] == address:
                        yield CancelFee(id, transaction['dateTime'], transaction['hash'], Ether.fee(transaction))
                    else:
                        contract = self.__getContractByAddress(transaction['to'])
                        if contract != None:
                            erc20Transaction = EtherscanApiReader.__getErc20Transaction(erc20Transactions, transaction['hash'])
                            yield from contract.processTransaction(address, id, transaction, erc20Transaction)
                        elif transaction['from'] == address:
                            yield WithdrawTransfer(id, transaction['dateTime'], transaction['hash'], Ether.amount(transaction), Ether.fee(transaction), transaction['to'])
                        elif transaction['to'] == address:
                            yield DepositTransfer(id, transaction['dateTime'], transaction['hash'], Ether.amount(transaction), Ether.zero(), transaction['from'])

    def __transformTransaction(self, transaction):
        transaction['dateTime'] = utc.localize(datetime.fromtimestamp(int(transaction['timeStamp'])))
        transaction['token'] = self.__getTokenByTransaction(transaction)
        return transaction

    def __getTokenByTransaction(self, transaction):
        token = self.__getTokenByAddress(transaction['from'])
        if token: return token
        token = self.__getTokenByAddress(transaction['to'])
        if token: return token
        return None

    def __getTokenByAddress(self, address):
        return self.__tokens[address] if address in self.__tokens else None

    def __getContractByAddress(self, address):
        return self.__closedSourceContracts[address] if address in self.__closedSourceContracts else None

    @staticmethod
    def __getErc20Transaction(transactions, hash):
        transaction = [t for t in transactions if t['hash'] == hash]
        return transaction[0] if len(transaction) > 0 else None
