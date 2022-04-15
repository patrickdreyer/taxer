from .banana.accounting import BananaAccounting
# from .shareholding.accounting import ShareholdingAccounting


class AccountingFactory:
    def __init__(self, args, config, currencyConverters):
        self.__args = args
        self.__config = config
        self.__currencyConverters = currencyConverters

    def create(self):
        return [
            BananaAccounting(self.__args.output, self.__config['accounting']['banana'], self.__currencyConverters)
            # ShareholdingAccounting(self.__args.input, self.__args.output, self.__args.year, self.__config, self.__currencyConverters)
        ]
