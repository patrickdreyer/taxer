from .v3Pool import V3Pool
from ..contract import Contract
from .....transactions.currency import Currency


class V3Pools:
    def __init__(self):
        self.__dict = {}

    def create(self, poolId:int, liquidity:int, contract0:Contract, contract1:Contract, amount0:Currency, amount1:Currency):
        self.__dict[poolId] = V3Pool(liquidity, contract0, contract1, amount0, amount1)

    def decrease(self, poolId:int, liquidity:int, amount0:str, amount1:str):
        if not poolId in self.__dict:
            raise KeyError(f"Non existing pool; id={poolId}")
        pool = self.__dict[poolId]
        amount0 = pool.contract0.amount(amount0)
        amount1 = pool.contract1.amount(amount1)
        if not pool.decrease(liquidity, amount0, amount1):
            self.__dict.pop(poolId)
        return (amount0, amount1)
