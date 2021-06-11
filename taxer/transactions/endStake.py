from .stake import Stake


class EndStake(Stake):
    def __init__(self, mergentId, dateTime, id, amount, fee):
        super().__init__(mergentId, dateTime, id, amount, fee)
