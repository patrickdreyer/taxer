import sys
import logging
import argparse
import time

from .mergents.mergents import Mergents
from .payments import Payments
from .currencyConverters.currencyConverters import CurrencyConverters
from .accounting.factory import AccountingFactory

class Application:
    __log = None

    def main(self):
        self.initializeLogging()

        Application.__log.info('BEGIN')
        args = self.parseArguments()
        mergents = Mergents(args.input)
        payments = Payments(args.input)
        currencyConverters = CurrencyConverters().load(args.cache)
        accounting = AccountingFactory(currencyConverters).create('Banana')
        self.process(mergents, payments, accounting, args.output)
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

    def process(self, mergents, payments, accounting, output):
        transactions = self.__readTransactions(mergents)
        transactions = payments.transform(transactions)
        accounting.write(transactions, output)

    def __readTransactions(self, mergents):
        readers = mergents.createReaders()
        for reader in readers:
            yield from reader.read()
