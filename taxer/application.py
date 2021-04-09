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
        self.initializeLogging()

        Application.__log.info('BEGIN')
        self.parseArguments()
        config = self.__readConfig()
        mergents = Mergents(config, self.__args.input)
        payments = Payments(self.__args.input)
        currencyConverters = CurrencyConverters().load(self.__args.cache)
        accounting = AccountingFactory(currencyConverters).create('Banana')
        self.process(mergents, payments, accounting, self.__args.output)
        currencyConverters.store(self.__args.cache)
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
        parser.add_argument('--config', type=str, help='File path to configuration')
        parser.add_argument('--year', type=str, help='Fiscal year to report')
        self.__args = parser.parse_args()

    def __readConfig(self):
        with open(self.__args.config, 'r') as file:
            return json.loads(file.read())

    def process(self, mergents, payments, accounting, output):
        transactions = self.__readTransactions(mergents)
        transactions = payments.transform(transactions)
        accounting.write(transactions, output)

    def __readTransactions(self, mergents):
        readers = mergents.createReaders()
        for reader in readers:
            yield from reader.read(int(self.__args.year))
