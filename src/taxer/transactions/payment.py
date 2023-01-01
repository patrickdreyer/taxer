from .transfer import Transfer


class Payment(Transfer):
    def __init__(self, withdrawTransfer, note):
        super().__init__(withdrawTransfer.mergentId, withdrawTransfer.dateTime, withdrawTransfer.id, withdrawTransfer.amount, withdrawTransfer.fee, None, note)
