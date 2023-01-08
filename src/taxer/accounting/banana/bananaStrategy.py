from ...container import Container
from .bananaCurrency import BananaCurrency


class BananaStrategy:
    def __init__(self, container:Container):
        self._container = container

    def initialize(self): pass
    def finalize(self): yield from []

    def doesTransform(self, transaction): pass
    def transform(self, transaction): pass

    def _currency(self, currency, mergentId, dateTime = None):
        return BananaCurrency(self._container, currency, mergentId, dateTime)

    def _book(self, transaction, args):
        pre = [transaction.dateTime.date().strftime('%d.%m.%Y'), transaction.id]
        return (transaction.dateTime.date(), pre + args)
