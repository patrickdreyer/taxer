from .stake import Stake


class StartStake(Stake):
    def __init__(self, mergentId, dateTime, id, stakeId, amount, fee):
        super().__init__(mergentId, dateTime, id, stakeId, amount, fee)
