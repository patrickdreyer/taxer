from decimal import Decimal
import re

from .contract import Contract
from ..ether import Ether
from ....transactions.currency import Currency
from ....transactions.swap import Swap


class MetamaskSwapRouterContract(Contract):
    __publicNameTag = 'Metamask: Swap Router'
    __address = '0x881d40237659c251811cec9c364ef91dc08d300c'
    __feeAddress = "0x11ededebf63bef0ea2d2d071bdf88f71543ec6fb"

    @property
    def address(self): return MetamaskSwapRouterContract.__address

    def __init__(self, contracts, etherscanApi):
        self.__etherscanApi = etherscanApi

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        if transaction['dateTime'].year != year:
            return

        name = MetamaskSwapRouterContract.__getFunction(transaction['functionName'])

        if name == 'swap':
            internalTransactions = self.__etherscanApi.getInternalTransactions(transaction['hash'])
            swappingTransaction = list(t for t in internalTransactions if t['from'] == self.__address)
            swappedTransaction = list(t for t in internalTransactions if t['to'] == address)
            feeTransaction = list(t for t in internalTransactions if t['to'] == MetamaskSwapRouterContract.__feeAddress)[0]
            if len(swappingTransaction) > 0:
                swapping = Ether.amountFromTransaction(swappingTransaction[0])
                swapped = MetamaskSwapRouterContract.__tokenAmount(erc20Transaction)
                fee = Ether.amountFromTransaction(feeTransaction)
                yield Swap(id, transaction['dateTime'], transaction['hash'], swapping, swapped, fee, MetamaskSwapRouterContract.__publicNameTag)
            elif len(swappedTransaction) > 0:
                swapping = MetamaskSwapRouterContract.__tokenAmount(erc20Transaction)
                swapped = Ether.amountFromTransaction(swappedTransaction[0])
                fee = Ether.amountFromTransaction(feeTransaction)
                yield Swap(id, transaction['dateTime'], transaction['hash'], swapping, swapped, fee, MetamaskSwapRouterContract.__publicNameTag)
            else:
                raise Exception(f"Unknown swapping; contract='{MetamaskSwapRouterContract.__publicNameTag}'")
        else:
            raise KeyError(f"Unknown contract function; contract='{MetamaskSwapRouterContract.__publicNameTag}', functionName='{name}'")

    @staticmethod
    def __getFunction(functionName):
        try:
            result = re.search(r"^([^(]+).*", functionName)
            return result.group(1).lower() if result != None else None
        except:
            return None

    @staticmethod
    def __tokenAmount(transaction):
        return Currency(transaction['tokenSymbol'], Decimal(transaction['value']) / Decimal('1' + '0'*int(transaction['tokenDecimal'])))
