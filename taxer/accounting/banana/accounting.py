from ..accounting import Accounting
from .transformer import BananaTransformer
from .accounts import BananaAccounts


class BananaAccounting(Accounting):
    __accounts = None
    __currencyConverter = None

    def __init__(self, currencyConverter):
        self.__accounts = BananaAccounts()
        self.__currencyConverter = currencyConverter

    def createTransformer(self):
        return BananaTransformer(self.__accounts, self.__currencyConverter)
