import sys
import logging
import argparse
import time

from .mergents.factory import MergentFactory
from .currencyConverters.currencyConverters import CurrencyConverters
from .accounting.factory import AccountingFactory

class Application:
    __log = None

    def main(self):
        self.initializeLogging()

        Application.__log.info('BEGIN')
        args = self.parseArguments()
        readers = MergentFactory().createFromPath(args.input)
        currencyConverters = CurrencyConverters().load(args.cache)
        accounting = AccountingFactory(currencyConverters).create('Banana')
        self.process(readers, accounting, args.output)
        currencyConverters.store(args.cache)
        Application.__log.info('END')

    def initializeLogging(self):
        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M',
            filename='taxer.log', filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        Application.__log = logging.getLogger(__name__)
        Application.__log.setLevel(logging.DEBUG)  

    def parseArguments(self):
        parser = argparse.ArgumentParser(description='Creates a CSV file ready to import into accounting from exchange reports')
        parser.add_argument('--input', type=str, help='Path to the directory containing the platform exports')
        parser.add_argument('--cache', type=str, default='cache', help='Path to the directory containing the cached data')
        parser.add_argument('--output', type=str, help='File name to write the output to')
        return parser.parse_args()

    def process(self, readers, accounting, output):
        transactions = self.reading(readers)
        accounting.write(transactions, output)

    def reading(self, readers):
        for reader in readers:
            yield from reader.read()
