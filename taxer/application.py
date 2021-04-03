import sys
import logging
import argparse
import time

from .mergents.factory import MergentFactory
from .currencyConverters.currencyConverter import CurrencyConverter
from .accounting.factory import AccountingFactory

class Application:
    __log = None

    def main(self):
        self.initializeLogging()

        self.__log.info('Started')
        args = self.parseArguments()
        readers = MergentFactory().createFromPath(args.input)
        currencyConverter = CurrencyConverter(args.input)
        accounting = AccountingFactory(currencyConverter).create('Banana')
        self.process(readers, accounting, args.output)
        self.__log.info('Stopped')

    def initializeLogging(self):
        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M',
            filename='taxer.log', filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        self.__log = logging.getLogger(__name__)
        self.__log.setLevel(logging.DEBUG)  

    def parseArguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('input', help='Path to the directory containing the platform exports')
        parser.add_argument('output', help='File name to write the output to')
        return parser.parse_args()

    def process(self, readers, accounting, output):
        transactions = self.reading(readers)
        transactions = sorted(transactions, key=lambda t: t.dateTime.timestamp())
        for transaction in transactions:
            accounting.transform(transaction)
        accounting.write(output)

    def reading(self, readers):
        for reader in readers:
            yield from reader.read()
