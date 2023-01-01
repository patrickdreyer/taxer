from .liquidityPool import LiquidityPool


class ClaimLiquidityFees(LiquidityPool):
    def __init__(self, mergentId, dateTime, id, amount0, amount1, fee, poolId, note=''):
        super().__init__(mergentId, dateTime, id, amount0, amount1, fee, poolId, note)
