class BananaStrategy:
    def __init__(self, config, accounts, currencyConverters): pass

    def initialize(self): pass
    def finalize(self): yield from []

    def doesTransform(self, transaction): pass
    def transform(self, transaction): pass

    @staticmethod
    def _createBooking(transaction, args):
        pre = [transaction.dateTime.date().strftime('%d.%m.%Y'), transaction.id]
        return (transaction.dateTime.date(), pre + args)
