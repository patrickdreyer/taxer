import csv
import logging
import os

from ...container import container
from ...pluginLoader import PluginLoader
from ..accounting import Accounting
from .bananaAccounts import BananaAccounts


class BananaAccounting(Accounting):
    __log = logging.getLogger(__name__)

    def __init__(self, config):
        container['banana'] = {
            'transferPrecision': config['transferPrecision'],
            'accounts': BananaAccounts(config['accounts'])
        }
        self.__fileNameBookings = config['fileNameBookings']
        self.__fileNameInterests = config['fileNameInterests']

    def write(self, transactions):
        path = os.path.join(os.path.dirname(__file__), 'strategies')
        self.__strategies = PluginLoader.loadFromFiles(path, f"{__package__}.strategies", '**/*Strategy.py', lambda clss: clss())
        self.__writeBookings(transactions)
        self.__writeInterests()

    def __writeBookings(self, transactions):
        outputFilePath = os.path.join(container['config']['output'], self.__fileNameBookings)
        bookings = self.__transform(transactions)
        bookings = sorted(bookings, key=lambda b: b[0])
        with open(outputFilePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['Datum', 'Beleg', 'Beschreibung', 'KtSoll', 'KtHaben', 'Betr.Währung', 'Währung', 'Wechselkurs', 'Betrag CHF', 'Anteile', 'Bemerkungen'])
            writer.writerows(booking[1] for booking in bookings)

    def __transform(self, transactions):
        for strategy in self.__strategies:
            strategy.initialize()

        for transaction in transactions:
            strategy = list([s for s in self.__strategies if s.doesTransform(transaction)])
            if len(strategy) != 1:
                BananaAccounting.__log.error("Unknown transaction; class='%s'", type(transaction).__name__)
                raise ValueError("Unknown transaction; type='{}'".format(type(transaction)))
            strategy = strategy[0]
            yield from strategy.transform(transaction)

        for strategy in self.__strategies:
            yield from strategy.finalize()

    def __writeInterests(self):
        outputFilePath = os.path.join(container['config']['output'], self.__fileNameInterests)
        interests = self.__collectInterests()
        with open(outputFilePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['Datum', 'Beleg', 'Beschreibung', 'Betr.Währung', 'Währung', 'Wechselkurs', 'Betrag CHF'])
            writer.writerows(interest[1] for interest in interests)

    def __collectInterests(self):
        for strategy in self.__strategies:
            yield from strategy.interests
