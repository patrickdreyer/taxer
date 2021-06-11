from .transfer import Transfer


class WithdrawTransfer(Transfer):
    def __init__(self, mergentId, dateTime, id, amount, fee):
        super().__init__(mergentId, dateTime, id, amount)
        self.__fee = fee

    @property
    def fee(self):
        return self.__fee

    def __str__(self):
        sup = super().__str__().replace('{', '').replace('}', '')
        return "{{{}, fee='{}'}}".format(sup, self.__fee)
