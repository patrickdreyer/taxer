from decimal import Decimal
import web3

from ...transactions.currency import Currency


class Ether:
    __divisor = 1000000000000000000

    @staticmethod
    def decodeContractInput(contract, input):
        try:
            ret = contract.decode_function_input(input)
            return (ret[0].fn_name.lower(), ret[1])
        except:
            return None

    @staticmethod
    def amount(transaction):
        return Currency('ETH', Decimal(transaction['value']) / Ether.__divisor)

    @staticmethod
    def fee(transaction):
        return Currency('ETH', Decimal(transaction['gasUsed']) * Decimal(transaction['gasPrice']) / Ether.__divisor)

    @staticmethod
    def zero():
        return Currency('ETH', 0)
