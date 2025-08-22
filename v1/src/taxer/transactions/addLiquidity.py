from .liquidityPool import LiquidityPool


class AddLiquidity(LiquidityPool):
    def __init__(self, mergentId, dateTime, id, amount0, amount0Wrapped, amount1, amount1Wrapped, fee, poolId, note=''):
        super().__init__(mergentId, dateTime, id, amount0, amount0Wrapped, amount1, amount1Wrapped, fee, poolId, note)
