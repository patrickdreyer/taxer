import argparse
import json
import logging
import sys
import time

from .mergents.mergents import Mergents
from .payments import Payments
from .currencyConverters.currencyConverters import CurrencyConverters
from .accounting.factory import AccountingFactory

class Application:
    __log = None

    def main(self):
        self.__initializeLogging()

        Application.__log.info('BEGIN')
        self.__parseArguments()
        self.__readConfig()
        self.__mergents = Mergents(self.__config, self.__args.input, self.__args.cache)
        self.__transformers = [Payments(self.__args.input)]
        self.__currencyConverters = CurrencyConverters().load(self.__args.cache)
        self.__accounting = AccountingFactory(self.__config, self.__currencyConverters).create('Banana')

        self.__process()

        self.__currencyConverters.store(self.__args.cache)
        Application.__log.info('END')

    def __initializeLogging(self):
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

    def __parseArguments(self):
        parser = argparse.ArgumentParser(description='Creates a CSV file ready to import into accounting from exchange reports')
        parser.add_argument('--input', type=str, help='Path to the directory containing the platform exports')
        parser.add_argument('--cache', type=str, default='cache', help='Path to the directory containing the cached data')
        parser.add_argument('--output', type=str, help='Path to write the output files to')
        parser.add_argument('--config', type=str, help='File path to configuration')
        parser.add_argument('--year', type=str, help='Fiscal year to report')
        self.__args = parser.parse_args()

    def __readConfig(self):
        with open(self.__args.config, 'r') as file:
            self.__config = json.load(file)

    def __process(self):
        transactions = self.__readTransactions()
        transactions = sorted(transactions, key=lambda t: t.dateTime)
        transactions = self.__transformTransactions(transactions)
        self.__accounting.write(transactions, self.__args.output)

    def __readTransactions(self):
        readers = self.__mergents.createReaders()
        for reader in readers:
            yield from reader.read(int(self.__args.year))

    def __transformTransactions(self, transactions):
        for transformer in self.__transformers:
            transactions = transformer.transform(transactions)
        return transactions
