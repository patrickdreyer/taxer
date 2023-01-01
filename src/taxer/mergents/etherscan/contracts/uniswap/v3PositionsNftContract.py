from web3 import Web3

from .v3Pools import V3Pools
from ..contract import Contract
from ...ether import Ether
from .....transactions.claimLiquidityFees import ClaimLiquidityFees
from .....transactions.createLiquidityPool import CreateLiquidityPool
from .....transactions.removeLiquidity import RemoveLiquidity


class V3PositionsNftContract(Contract):
    __publicNameTag = 'Uniswap V3: Positions NFT'
    __address = '0xc36442b4a4522e871399cd717abdd847ab11fe88'
    __increaseLiquidityTopic = '0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f'
    __collectTopic = '0x40d0efd1a53d60ecbf40971b9daf7dc90178c3aadc7aab1765632738fa8b8f01'

    @property
    def address(self): return V3PositionsNftContract.__address

    def __init__(self, contracts, etherscanApi):
        self.__etherscanApi = etherscanApi
        self.__contracts = contracts
        self.__pools = V3Pools()
        self.__web3Contract = etherscanApi.getContract(V3PositionsNftContract.__address)

    def processTransaction(self, address, id, year, transaction, erc20Transaction):
        (name, args) = Ether.decodeContractInput(self.__web3Contract, transaction['input'])

        if name == 'multicall':
            (name, args) = Ether.decodeContractInput(self.__web3Contract, args['data'][0])
            if name == 'mint':
                yield from self.__mint(year, transaction, args)
            elif name == 'decreaseliquidity':
                poolId = int(args['params'][0])
                (amount0, amount1) = self.__pools.decrease(poolId, args['params'][1], args['params'][2], args['params'][3])
                if transaction['dateTime'].year == year:
                    fee = Ether.amountFromTransaction(transaction)
                    yield RemoveLiquidity(id, transaction['dateTime'], transaction['hash'], amount0, amount1, fee, poolId, V3PositionsNftContract.__publicNameTag)
            elif name == 'collect':
                if transaction['dateTime'].year == year:
                    poolId = int(args['params'][0])
                    collectLog = self.__etherscanApi.getLogsByTopic(transaction['blockNumber'], address, V3PositionsNftContract.__collectTopic)[0]
                    output = Ether.decodeContractEventData(self.__web3Contract, 'Collect', collectLog['topics'], collectLog['data'])
                    (amount0, amount1) = self.__pools.collect(poolId, output['amount0'], output['amount1'])
                    fee = Ether.amountFromTransaction(transaction)
                    yield ClaimLiquidityFees(id, transaction['dateTime'], transaction['hash'], amount0, amount1, fee, poolId, V3PositionsNftContract.__publicNameTag)
            else:
                raise KeyError(f"Unknown contract multicall function; contract='{V3PositionsNftContract.__publicNameTag}', functionName='multicall.{name}'")
        elif name == 'mint':
            yield from self.__mint(year, transaction, args)
        else:
            raise KeyError(f"Unknown contract function; contract='{V3PositionsNftContract.__publicNameTag}', functionName='{name}'")

    def __mint(self, year, transaction, args):
        contract0 = self.__contracts.getByAddress(args['params'][0])
        contract1 = self.__contracts.getByAddress(args['params'][1])

        increaseLiquidityLog = self.__etherscanApi.getLogsByTopic(transaction['blockNumber'], V3PositionsNftContract.__address, V3PositionsNftContract.__increaseLiquidityTopic)[0]
        output = Ether.decodeContractFunctionData(self.__web3Contract, 'increaseLiquidity', increaseLiquidityLog['data'])
        poolId = Web3.toInt(hexstr=increaseLiquidityLog['topics'][1])
        liquidity = output['liquidity']
        amount0 = contract0.amount(output['amount0'])
        amount1 = contract1.amount(output['amount1'])
        fee = Ether.amountFromTransaction(transaction)
        self.__pools.create(poolId, liquidity, contract0, contract1, amount0, amount1)
        if transaction['dateTime'].year == year:
            yield CreateLiquidityPool(id, transaction['dateTime'], transaction['hash'], amount0, amount1, fee, poolId, V3PositionsNftContract.__publicNameTag)
