from decimal import Decimal
from eth_abi import decode
import web3

from ...transactions.currency import Currency


class Pulse:
    __divisor = 1000000000000000000

    @staticmethod
    def decodeContractInput(decodedInput):
        try:
            name = decodedInput['method_call'].split('(', 1)[0].lower()
            args = {}
            for p in decodedInput['parameters']:
                args[p['name']] = p['value']
            return (name, args)
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
    def decodeContractEventData(contract:web3.contract.Contract, name:str, topics, data:str):
        events = [e for e in contract.events.abi if 'name' in e and e['name'] == name]
        if not events:
            raise KeyError(f"Event name not found; contract='{contract.name}', event='{name}'")
        inputs = events[0]['inputs']
        ret = {}

        topicInputs = [i for i in inputs if i['indexed']]
        for i, value in enumerate(topics[1:]): # always skip topic0
            ret[topicInputs[i]['name']] = value

        dataInputs = [i for i in inputs if not i['indexed']]
        dataTypes = [i['type'] for i in dataInputs]
        dataBytes = web3.Web3.toBytes(hexstr=data)
        values = decode(dataTypes, dataBytes)
        for i, value in enumerate(values):
            ret[dataInputs[i]['name']] = value

        return ret

    @staticmethod
    def amountFromTransaction(transaction):
        return Pulse.amount(transaction['value'])

    @staticmethod
    def amount(value):
        return Currency('PLS', Decimal(value) / Pulse.__divisor)

    @staticmethod
    def feeFromTransaction(transaction):
        return Currency('PLS', Decimal(transaction['gas_used']) * Decimal(transaction['gas_price']) / Pulse.__divisor)

    @staticmethod
    def zero():
        return Currency('PLS', 0)

    @staticmethod
    def toTopic(address):
        if not isinstance(address, str):
            address = hex(address)
        elif isinstance(address, str) and address[:2].lower() != '0x':
            address = hex(int(address))
        address = address.replace('0x', '')
        return f"0x{address:0>64}"
