from ..contract import Contract
from ...ether import Ether
from .....transactions.currency import Currency
from .....transactions.swap import Swap


class V3RouterContract(Contract):
    @property
    def web3Contract(self): return self.__web3Contract

    def __init__(self, contracts, accounts:list[str], etherscanApi):
        super().__init__('0xE592427A0AEce92De3Edee1F18E0157C05861564', 'Uniswap V3: Router', accounts)
        self.__etherscanApi = etherscanApi
        self.__contracts = contracts
        self.__web3Contract = etherscanApi.getContract(self.address)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        if transaction['dateTime'].year != year:
            return

        (name, args) = Ether.decodeContractInput(self.__web3Contract, transaction['input'])
        if name == 'multicall':
            (name, args) = Ether.decodeContractInput(self.__web3Contract, args['data'][0])
            if name == 'exactinput':
                yield from self.__exactInput(address, id, transaction)
            else:
                yield from self.__exactOutput(address, id, transaction)
        elif name == 'exactinput':
            yield from self.__exactInput(address, id, transaction)
        else:
            raise KeyError(f"Unknown contract function; contract='{self.publicNameTag}', functionName='{name}'")

    def amount(self, value) -> Currency:
        raise NotImplementedError('V3RouterContract.amount() not supported')

    def __exactInput(self, address, id, transaction):
        swapping = Ether.amountFromTransaction(transaction)
        if swapping.amount > 0:
            # ETH -> Token
            swapped = self.__getSwappedAmount(address, transaction)
        else:
            # Token -> ETH
            swappingTransferLog = self.__etherscanApi.getFirstLog(transaction['blockNumber'], topic1 = Ether.toTopic(address))
            swappingContract = self.__contracts.getByAddress(swappingTransferLog['address'])
            swappingOutput = Ether.decodeContractEventData(swappingContract.web3Contract, 'Transfer', swappingTransferLog['topics'], swappingTransferLog['data'])
            swapping = swappingContract.amount(swappingOutput['value'])
            internalTransaction = [it for it in self.__etherscanApi.getInternalTransactions(transaction['hash']) if it['to'] == address][0]
            swapped = Ether.amount(internalTransaction['value'])
        #TODO Token -> Token

        fee = Ether.feeFromTransaction(transaction)
        yield Swap(id, transaction['dateTime'], transaction['hash'], swapping, swapped, fee, self.publicNameTag)

    def __exactOutput(self, address, id, transaction):
        internalTransaction = [it for it in self.__etherscanApi.getInternalTransactions(transaction['hash']) if it['to'] == address][0]
        payback = Ether.amount(internalTransaction['value'])
        swapping = Ether.amountFromTransaction(transaction) - payback
        swapped = self.__getSwappedAmount(address, transaction)
        fee = Ether.feeFromTransaction(transaction)
        yield Swap(id, transaction['dateTime'], transaction['hash'], swapping, swapped, fee, self.publicNameTag)

    def __getSwappedAmount(self, address, transaction):
        swappedTransferLog = self.__etherscanApi.getFirstLog(transaction['blockNumber'], topic2 = Ether.toTopic(address))
        swappedContract = self.__contracts.getByAddress(swappedTransferLog['address'])
        swappedOutput = Ether.decodeContractEventData(swappedContract.web3Contract, 'Transfer', swappedTransferLog['topics'], swappedTransferLog['data'])
        return swappedContract.amount(swappedOutput['value'])
