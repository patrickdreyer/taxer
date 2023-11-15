from web3 import Web3

from .v3Pools import V3Pools
from ..contract import Contract
from ...ether import Ether
from .....transactions.addLiquidity import AddLiquidity
from .....transactions.claimLiquidityFees import ClaimLiquidityFees
from .....transactions.createLiquidityPool import CreateLiquidityPool
from .....transactions.currency import Currency
from .....transactions.removeLiquidity import RemoveLiquidity


class V3PositionsNftContract(Contract):
    __increaseLiquidityTopic = '0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f'
    __decreaseLiquidityLogTopic = '0x26f6a048ee9138f2c0ce266f322cb99228e8d619ae2bff30c67f8dcf9d2377b4'
    __collectTopic = '0x40d0efd1a53d60ecbf40971b9daf7dc90178c3aadc7aab1765632738fa8b8f01'

    @property
    def web3Contract(self): return self.__web3Contract

    def __init__(self, contracts, accounts:list[str], etherscanApi):
        super().__init__('0xC36442b4a4522E871399CD717aBDD847Ab11FE88', 'Uniswap V3: Positions NFT', accounts)
        self.__etherscanApi = etherscanApi
        self.__contracts = contracts
        self.__pools = V3Pools()
        self.__web3Contract = etherscanApi.getContract(self.address)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        (name, args) = Ether.decodeContractInput(self.__web3Contract, transaction['input'])
        if name == 'multicall':
            (innerName, innerArgs) = Ether.decodeContractInput(self.__web3Contract, args['data'][0])
            if innerName == 'mint':
                yield from self.__mint(id, year, transaction, innerArgs)
            elif innerName == 'increaseliquidity':
                poolId = int(innerArgs['params'][0])
                increaseliquidityLog = self.__etherscanApi.getFirstLog(transaction['blockNumber'], address = self.address, topic0 = V3PositionsNftContract.__increaseLiquidityTopic, topic1 = Ether.toTopic(poolId))
                output = Ether.decodeContractEventData(self.__web3Contract, 'IncreaseLiquidity', increaseliquidityLog['topics'], increaseliquidityLog['data'])
                (amount0Wrapped, amount1Wrapped) = self.__pools.increase(poolId, output['liquidity'], output['amount0'], output['amount1'])
                amount0 = self.__unwrapWETH(amount0Wrapped)
                amount1 = self.__unwrapWETH(amount1Wrapped)
                if transaction['dateTime'].year == year:
                    fee = Ether.feeFromTransaction(transaction)
                    yield AddLiquidity(id, transaction['dateTime'], transaction['hash'], amount0, amount0Wrapped, amount1, amount1Wrapped, fee, poolId, self.publicNameTag)
            elif innerName == 'decreaseliquidity':
                poolId = int(innerArgs['params'][0])
                decreaseLiquidityLog = self.__etherscanApi.getFirstLog(transaction['blockNumber'], address = self.address, topic0 = V3PositionsNftContract.__decreaseLiquidityLogTopic, topic1 = Ether.toTopic(poolId))
                output = Ether.decodeContractEventData(self.__web3Contract, 'DecreaseLiquidity', decreaseLiquidityLog['topics'], decreaseLiquidityLog['data'])
                liquidity = output['liquidity']
                collectLog = self.__etherscanApi.getFirstLog(transaction['blockNumber'], address = self.address, topic0 = V3PositionsNftContract.__collectTopic, topic1 = Ether.toTopic(poolId))
                output = Ether.decodeContractEventData(self.__web3Contract, 'Collect', collectLog['topics'], collectLog['data'])
                (amount0Wrapped, amount1Wrapped) = self.__pools.decrease(poolId, liquidity, output['amount0'], output['amount1'])
                amount0 = self.__unwrap(amount0Wrapped, args['data'])
                amount1 = self.__unwrap(amount1Wrapped, args['data'])
                if transaction['dateTime'].year == year:
                    fee = Ether.feeFromTransaction(transaction)
                    yield RemoveLiquidity(id, transaction['dateTime'], transaction['hash'], amount0, amount0Wrapped, amount1, amount1Wrapped, fee, poolId, self.publicNameTag)
            elif innerName == 'collect':
                if transaction['dateTime'].year == year:
                    poolId = int(innerArgs['params'][0])
                    collectLog = self.__etherscanApi.getFirstLog(transaction['blockNumber'], address = self.address, topic0 = V3PositionsNftContract.__collectTopic, topic1 = Ether.toTopic(poolId))
                    output = Ether.decodeContractEventData(self.__web3Contract, 'Collect', collectLog['topics'], collectLog['data'])
                    (amount0Wrapped, amount1Wrapped) = self.__pools.collect(poolId, output['amount0'], output['amount1'])
                    amount0 = self.__unwrap(amount0Wrapped, args['data'])
                    amount1 = self.__unwrap(amount1Wrapped, args['data'])
                    fee = Ether.feeFromTransaction(transaction)
                    yield ClaimLiquidityFees(id, transaction['dateTime'], transaction['hash'], amount0, amount0Wrapped, amount1, amount1Wrapped, fee, poolId, self.publicNameTag)
            else:
                raise KeyError(f"Unknown contract multicall function; contract='{self.publicNameTag}', functionName='multicall.{innerName}'")
        elif name == 'mint':
            yield from self.__mint(id, year, transaction, args)
        else:
            raise KeyError(f"Unknown contract function; contract='{self.publicNameTag}', functionName='{name}'")

    def __mint(self, id, year, transaction, args):
        contract0 = self.__contracts.getByAddress(args['params'][0])
        contract1 = self.__contracts.getByAddress(args['params'][1])

        increaseLiquidityLog = self.__etherscanApi.getFirstLog(transaction['blockNumber'], address = self.address, topic0 = V3PositionsNftContract.__increaseLiquidityTopic)
        output = Ether.decodeContractFunctionData(self.__web3Contract, 'increaseLiquidity', increaseLiquidityLog['data'])
        poolId = Web3.toInt(hexstr=increaseLiquidityLog['topics'][1])
        liquidity = output['liquidity']
        amount0Wrapped = contract0.amount(output['amount0'])
        amount1Wrapped = contract1.amount(output['amount1'])
        amount0 = self.__unwrapWETH(amount0Wrapped)
        amount1 = self.__unwrapWETH(amount1Wrapped)
        fee = Ether.feeFromTransaction(transaction)
        self.__pools.create(poolId, liquidity, contract0, contract1, amount0Wrapped, amount1Wrapped)
        if transaction['dateTime'].year == year:
            yield CreateLiquidityPool(id, transaction['dateTime'], transaction['hash'], amount0, amount0Wrapped, amount1, amount1Wrapped, fee, poolId, self.publicNameTag)

    def __unwrapWETH(self, amount):
        return Currency('ETH', amount.amount) if amount.unit == 'WETH' else amount

    def __unwrap(self, amount, contractInputs):
        for contractInput in contractInputs:
            (name, _) = Ether.decodeContractInput(self.__web3Contract, contractInput)
            if name == 'unwrapweth9':
                return self.__unwrapWETH(amount)
        return amount
