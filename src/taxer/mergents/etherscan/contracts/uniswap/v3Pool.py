from ..contract import Contract
from .....transactions.currency import Currency


class V3Pool:
    def __init__(self, liquidity:int, contract0:Contract, contract1:Contract, amount0:Currency, amount1:Currency):
        self.__liquidity = liquidity
        self.__contract0 = contract0
        self.__contract1 = contract1
        self.__amount0 = amount0
        self.__amount1 = amount1

    @property
    def contract0(self): return self.__contract0

    @property
    def contract1(self): return self.__contract1

    def decrease(self, liquidity:int, amount0:Currency, amount1:Currency):
        self.__liquidity -= liquidity
        if self.__liquidity == 0:
            return False
        self.__amount0 = self.__amount0 - amount0
        self.__amount1 = self.__amount1 - amount1
        return True
