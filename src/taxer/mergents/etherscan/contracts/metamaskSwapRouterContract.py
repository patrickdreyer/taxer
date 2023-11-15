from decimal import Decimal
import re

from .contract import Contract
from ..ether import Ether
from ....transactions.currency import Currency
from ....transactions.swap import Swap


class MetamaskSwapRouterContract(Contract):
    __feeAddress = "0x11ededebf63bef0ea2d2d071bdf88f71543ec6fb"

    def __init__(self, contracts, accounts:list[str], etherscanApi):
        super().__init__('0x881D40237659C251811CEC9c364ef91dC08D300C', 'Metamask: Swap Router', accounts)
        self.__etherscanApi = etherscanApi

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        if transaction['dateTime'].year != year:
            return

        name = MetamaskSwapRouterContract.__getFunction(transaction['functionName'])

        if name == 'swap':
            internalTransactions = self.__etherscanApi.getInternalTransactions(transaction['hash'])
            swappingTransaction = list(t for t in internalTransactions if t['from'].lower() == self.address.lower())
            swappedTransaction = list(t for t in internalTransactions if t['to'].lower() == address.lower())
            feeTransaction = list(t for t in internalTransactions if t['to'].lower() == MetamaskSwapRouterContract.__feeAddress)[0]
            if len(swappingTransaction) > 0:
                blockchainFee = Ether.feeFromTransaction(transaction)
                metamaskFee = Ether.amountFromTransaction(feeTransaction)
                fee = blockchainFee + metamaskFee
                swapping = Ether.amountFromTransaction(swappingTransaction[0]) - metamaskFee
                swapped = MetamaskSwapRouterContract.__tokenAmount(erc20Transaction)
                yield Swap(id, transaction['dateTime'], transaction['hash'], swapping, swapped, fee, self.publicNameTag)
            elif len(swappedTransaction) > 0:
                blockchainFee = Ether.feeFromTransaction(transaction)
                metamaskFee = Ether.amountFromTransaction(feeTransaction)
                fee = blockchainFee + metamaskFee
                swapping = MetamaskSwapRouterContract.__tokenAmount(erc20Transaction)
                swapped = Ether.amountFromTransaction(swappedTransaction[0]) + metamaskFee
                yield Swap(id, transaction['dateTime'], transaction['hash'], swapping, swapped, fee, self.publicNameTag)
            else:
                raise Exception(f"Unknown swapping; contract='{self.publicNameTag}'")
        else:
            raise KeyError(f"Unknown contract function; contract='{self.publicNameTag}', functionName='{name}'")

    def amount(self, value) -> Currency:
        raise NotImplementedError('MetamaskSwapRouterContract.amount() not supported')

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
