from .stake import Stake


class EndStake(Stake):
    def __init__(self, mergentId, dateTime, id, stakeId, principal, interest, total, fee):
        super().__init__(mergentId, dateTime, id, stakeId, principal, fee)
        self.__interest = interest
        self.__total = total

    @property
    def interest(self):
        return self.__interest

    @property
    def total(self):
        return self.__total
