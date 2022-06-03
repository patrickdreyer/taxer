import argparse
import json
import logging
import os
import pickle

from .accounting.accountingfactory import AccountingFactory
from .currencyConverters.currencyConverterFactory import CurrencyConverterFactory
from .mergents.mergentFactory import MergentFactory
from .transformers.transformerFactory import TransformerFactory

class Application:
    __transactionsFileName = 'transactions.json'
    __log = None

    def main(self):
        self.__initializeLogging()

        Application.__log.info('BEGIN')
        self.__parseArguments()
        self.__readConfig()
        self.__mergents = MergentFactory.create(self.__config, self.__args.input, self.__args.cache)
        self.__transformers = TransformerFactory.create(self.__config)
        self.__currencyConverters = CurrencyConverterFactory.create(self.__config, self.__args.cache).load()
        self.__accountings = AccountingFactory.create(self.__args, self.__config, self.__currencyConverters)

        self.__process()

        self.__currencyConverters.store()
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
        parser.add_argument('--transactions', type=str, help='File path to import transactions from or export transactions to')
        self.__args = parser.parse_args()

    def __readConfig(self):
        with open(self.__args.config, 'r') as file:
            self.__config = json.load(file)

    def __process(self):
        transactions = self.__deserializeTransactions()
        if transactions == None:
            transactions = (t for t in self.__readTransactions() if t != None)
            transactions = sorted(transactions, key=lambda t: t.dateTime)
            self.__serializeTransactions(transactions)
        for accounting in self.__accountings:
            transactions = list(self.__transformTransactions(transactions))
            accounting.write(transactions)

    def __readTransactions(self):
        readers = self.__mergents.createReaders()
        for reader in readers:
            yield from reader.read(int(self.__args.year))

    def __transformTransactions(self, transactions):
        for transformer in self.__transformers:
            transactions = transformer.transform(transactions)
        return transactions

    def __serializeTransactions(self, transactions):
        if not self.__args.transactions:
            return
        Application.__log.info("Serialize transactions; filePath='%s'", self.__args.transactions)
        with open(os.path.join(self.__args.transactions, Application.__transactionsFileName), 'wb') as file:
            pickle.dump(transactions, file)

    def __deserializeTransactions(self):
        if not self.__args.transactions:
            return None
        filePath = os.path.join(self.__args.transactions, Application.__transactionsFileName)
        if not os.path.isfile(filePath):
            return None
        Application.__log.info("Deserialize transactions; filePath='%s'", filePath)
        with open(filePath, 'rb') as file:
            return pickle.load(file)
