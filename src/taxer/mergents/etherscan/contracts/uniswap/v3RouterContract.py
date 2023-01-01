from web3 import Web3

from ..contract import Contract
from ...ether import Ether
from .....transactions.swap import Swap


class V3RouterContract(Contract):
    __publicNameTag = 'Uniswap V3: Router'
    __address = '0xE592427A0AEce92De3Edee1F18E0157C05861564'

    @property
    def address(self): return V3RouterContract.__address

    @property
    def web3Contract(self): return self.__web3Contract

    def __init__(self, contracts, etherscanApi):
        self.__etherscanApi = etherscanApi
        self.__contracts = contracts
        self.__web3Contract = etherscanApi.getContract(V3RouterContract.__address)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        if transaction['dateTime'].year != year:
            return

        (name, args) = Ether.decodeContractInput(self.__web3Contract, transaction['input'])

        if name == 'exactinput':
            swapping = Ether.amountFromTransaction(transaction)
            if swapping.amount == 0:
                raise NotImplementedError(f"Swapping from non ETH not yet supported; contract='{V3RouterContract.__publicNameTag}'")

            transferAmount1Log = self.__etherscanApi.getLogsByTopic2(transaction['blockNumber'], Ether.toTopic(address))[0]
            contract1 = self.__contracts.getByAddress(transferAmount1Log['address'])
            output = Ether.decodeContractEventData(contract1.web3Contract, 'Transfer', transferAmount1Log['topics'], transferAmount1Log['data'])
            swapped = contract1.amount(output['value'])

            fee = Ether.feeFromTransaction(transaction)

            yield Swap(id, transaction['dateTime'], transaction['hash'], swapping, swapped, fee, V3RouterContract.__publicNameTag)
        else:
            raise KeyError(f"Unknown contract function; contract='{V3RouterContract.__publicNameTag}', functionName='{name}'")
