from decimal import Decimal
from eth_abi import decode
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
            return (None, None)

    @staticmethod
    def decodeContractFunctionData(contract:web3.contract.Contract, name:str, data:str):
        function = contract.get_function_by_name(name)
        outputs = function.abi['outputs']
        types = [o['type'] for o in outputs]
        dataBytes = web3.Web3.toBytes(hexstr=data)
        values = decode(types, dataBytes)
        return {outputs[i]['name']:value for i, value in enumerate(values)}

    @staticmethod
    def amountFromTransaction(transaction):
        return Ether.amount(transaction['value'])

    @staticmethod
    def amount(value):
        return Currency('ETH', Decimal(value) / Ether.__divisor)

    @staticmethod
    def feeFromTransaction(transaction):
        return Currency('ETH', Decimal(transaction['gasUsed']) * Decimal(transaction['gasPrice']) / Ether.__divisor)

    @staticmethod
    def zero():
        return Currency('ETH', 0)
