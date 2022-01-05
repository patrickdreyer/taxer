from .banana.accounting import BananaAccounting
from .shareholder.accounting import ShareholderAccounting


class AccountingFactory:
    def __init__(self, args, config, currencyConverters):
        self.__args = args
        self.__config = config
        self.__currencyConverters = currencyConverters

    def create(self):
        return [
            # BananaAccounting(self.__args.output, self.__config['accounting'], self.__currencyConverters),
            ShareholderAccounting(self.__args.input, self.__args.output, int(self.__args.year), self.__config['accounting'], self.__currencyConverters)
        ]
