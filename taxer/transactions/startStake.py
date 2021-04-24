from .stake import Stake


class StartStake(Stake):
    def __init__(self, mergentId, dateTime, id, unitAmount, amount, unitFee, fee):
        super().__init__(mergentId, dateTime, id, unitAmount, amount, unitFee, fee)
