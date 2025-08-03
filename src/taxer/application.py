import argparse
import json
import logging
import os
import pickle

from .container import container
from .accounting.accountingfactory import AccountingFactory
from .currencyConverters.currencyConverterFactory import CurrencyConverterFactory
from .mergents.mergentFactory import MergentFactory
from .transformers.transformerFactory import TransformerFactory


class Application:
    __log = None
    __transactionsFileName = 'transactions.json'

    def main(self):
        self.__initializeLogging()

        Application.__log.info('BEGIN')
        container['config'] = self.__parseArguments()
        container['config'] = container['config'] | self.__readConfig()
        container['mergents'] = MergentFactory.create()
        container['transformers'] = TransformerFactory.create()
        container['currencyConverters'] = CurrencyConverterFactory.create().load()
        container['accountings'] = AccountingFactory.create()
        container['mergentReaders'] = lambda container: list(container['mergents'].createReaders())

        self.__process()

        container['currencyConverters'].store()
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
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def __parseArguments(self):
        parser = argparse.ArgumentParser(description='Creates a CSV file ready to import into accounting from exchange reports')
        parser.add_argument('--input', type=str, help='Path to the directory containing the platform exports')
        parser.add_argument('--cache', type=str, default='cache', help='Path to the directory containing the cached data')
        parser.add_argument('--output', type=str, help='Path to write the output files to')
        parser.add_argument('--config', type=str, help='File path to configuration')
        parser.add_argument('--year', type=str, help='Fiscal year to report')
        parser.add_argument('--transactions', type=str, help='File path to import transactions from or export transactions to')
        namespace = parser.parse_args()
        return vars(namespace)

    def __readConfig(self) -> any:
        with open(container['config']['config'], 'r') as file:
            return json.load(file)

    def __process(self):
        transactions = self.__readTransactions()
        transactions = list(self.__transform(transactions))
        for accounting in container['accountings']:
            accounting.write(transactions)

    def __readTransactions(self):
        transactions = self.__deserializeTransactions()
        if transactions == None:
            transactions = (t for t in self.__readFromMergenReaders() if t != None)
            transactions = sorted(transactions, key=lambda t: t.dateTime)
            self.__serializeTransactions(transactions)

    def __serializeTransactions(self, transactions):
        if not container['config']['transactions']:
            return
        Application.__log.info("Serialize transactions; filePath='%s'", container['config']['transactions'])
        if not os.path.exists(container['config']['transactions']):
            os.makedirs(container['config']['transactions'])
        with open(os.path.join(container['config']['transactions'], Application.__transactionsFileName), 'wb') as file:
            pickle.dump(transactions, file)

    def __deserializeTransactions(self):
        if not container['config']['transactions']:
            return None
        filePath = os.path.join(container['config']['transactions'], Application.__transactionsFileName)
        if not os.path.isfile(filePath):
            return None
        Application.__log.info("Deserialize transactions; filePath='%s'", filePath)
        with open(filePath, 'rb') as file:
            return pickle.load(file)

    def __readFromMergenReaders(self):
        readers = container['mergentReaders']
        year = int(container['config']['year'])
        for reader in readers:
            yield from reader.read(year)

    def __transform(self, transactions):
        for transformer in container['transformers']:
            transactions = transformer.transform(transactions)
        return transactions
