import csv
import logging
import os

from ...pluginLoader import PluginLoader
from ..accounting import Accounting
from .bananaAccounts import BananaAccounts


class BananaAccounting(Accounting):
    __fileName = 'banana.csv'

    __log = logging.getLogger(__name__)

    def __init__(self, output, config, currencyConverters):
        self.__output = output
        self.__config = config
        self.__accounts = BananaAccounts(config['accounts'])
        self.__currencyConverters = currencyConverters

    def write(self, transactions):
        outputFilePath = os.path.join(self.__output, BananaAccounting.__fileName)
        bookings = self.__transform(transactions)
        bookings = sorted(bookings, key=lambda b: b[0])
        with open(outputFilePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['Datum', 'Beleg', 'Beschreibung', 'KtSoll', 'KtHaben', 'Betr.Währung', 'Währung', 'Wechselkurs', 'Betrag CHF', 'Anteile', 'KS1', 'Bemerkungen'])
            writer.writerows(booking[1] for booking in bookings)

    def __transform(self, transactions):
        path = os.path.join(os.path.dirname(__file__), 'strategies')
        strategies = PluginLoader.loadFromFiles(path, f"{__package__}.strategies", '**/*Strategy.py', lambda clss: clss(self.__config, self.__accounts, self.__currencyConverters))

        for strategy in strategies:
            strategy.initialize()

        for transaction in transactions:
            transaction['bananaDate'] = BananaAccounting.__getDate(transaction)
            strategy = list([s for s in strategies if s.doesTransform(transaction)])
            if len(strategy) != 1:
                BananaAccounting.__log.error("Unknown transaction; class='%s'", type(transaction).__name__)
                raise ValueError("Unknown transaction; type='{}'".format(type(transaction)))
            strategy = strategy[0]
            yield from strategy.transform(transaction)

        for strategy in strategies:
            yield from strategy.finalize()

    @staticmethod
    def __getDate(transaction):
        return [transaction.dateTime.date(), transaction.dateTime.date().strftime('%d.%m.%Y')]
