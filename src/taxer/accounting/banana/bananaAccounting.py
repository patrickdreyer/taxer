import csv
import logging
import os

from ...container import Container
from ...pluginLoader import PluginLoader
from ..accounting import Accounting
from .bananaAccounts import BananaAccounts


class BananaAccounting(Accounting):
    __log = logging.getLogger(__name__)

    def __init__(self, container:Container, config):
        self.__container = container
        self.__container['banana'] = {
            'transferPrecision': config['transferPrecision'],
            'accounts': BananaAccounts(config['accounts'])
        }
        self.__fileName = config['fileName']

    def write(self, transactions):
        outputFilePath = os.path.join(self.__container['config']['output'], self.__fileName)
        bookings = self.__transform(transactions)
        bookings = sorted(bookings, key=lambda b: b[0])
        with open(outputFilePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['Datum', 'Beleg', 'Beschreibung', 'KtSoll', 'KtHaben', 'Betr.Währung', 'Währung', 'Wechselkurs', 'Betrag CHF', 'Anteile', 'KS1', 'Bemerkungen'])
            writer.writerows(booking[1] for booking in bookings)

    def __transform(self, transactions):
        path = os.path.join(os.path.dirname(__file__), 'strategies')
        strategies = PluginLoader.loadFromFiles(path, f"{__package__}.strategies", '**/*Strategy.py', lambda clss: clss(self.__container))

        for strategy in strategies:
            strategy.initialize()

        for transaction in transactions:
            strategy = list([s for s in strategies if s.doesTransform(transaction)])
            if len(strategy) != 1:
                BananaAccounting.__log.error("Unknown transaction; class='%s'", type(transaction).__name__)
                raise ValueError("Unknown transaction; type='{}'".format(type(transaction)))
            strategy = strategy[0]
            yield from strategy.transform(transaction)

        for strategy in strategies:
            yield from strategy.finalize()
