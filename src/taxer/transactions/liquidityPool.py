from .transaction import Transaction


class LiquidityPool(Transaction):
    def __init__(self, mergentId, dateTime, id, amount0, amount1, fee, poolId, note=''):
        super().__init__(mergentId, dateTime, id, note)
        self.__amount0 = amount0
        self.__amount1 = amount1
        self.__fee = fee
        self.__poolId = poolId

    @property
    def amount0(self):
        return self.__amount0

    @property
    def amount1(self):
        return self.__amount1

    @property
    def fee(self):
        return self.__fee

    @property
    def poolId(self):
        return self.__poolId

    def __str__(self):
        sup = super().__str__().replace('{', '').replace('}', '')
        return f"{{{sup}, amount0={self.__amount0}, amount1={self.__amount1}, fee={self.__fee}, poolId={self.__poolId}}}"
