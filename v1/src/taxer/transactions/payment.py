from .transfer import Transfer


class Payment(Transfer):
    def __init__(self, mergentId, dateTime, id, amount, fee, note):
        super().__init__(mergentId, dateTime, id, amount, fee, None, note)
