from .transfer import Transfer


class WithdrawTransfer(Transfer):
    def __init__(self, mergentId, dateTime, id, unit, amount, fee):
        super().__init__(mergentId, dateTime, id, unit, amount)
        self.__fee = fee

    @property
    def fee(self):
        return self.__fee
