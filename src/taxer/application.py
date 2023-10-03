import argparse
import json
import logging

from .accounting.accountingfactory import AccountingFactory
from .container import Container
from .currencyConverters.currencyConverterFactory import CurrencyConverterFactory
from .mergents.mergentFactory import MergentFactory
from .processors.processorFactory import ProcessorFactory
from .transformers.transformerFactory import TransformerFactory


class Application:
    __log = None

    def main(self):
        self.__initializeLogging()

        Application.__log.info('BEGIN')
        self.__container = Container()
        self.__container['config'] = self.__parseArguments()
        self.__container['config'] = self.__container['config'] | self.__readConfig()
        self.__container['processors'] = ProcessorFactory.create(self.__container)
        self.__container['mergents'] = MergentFactory.create(self.__container)
        self.__container['transformers'] = TransformerFactory.create(self.__container)
        self.__container['currencyConverters'] = CurrencyConverterFactory.create(self.__container).load()
        self.__container['accountings'] = AccountingFactory.create(self.__container)
        self.__container['mergentReaders'] = lambda container: list(container['mergents'].createReaders())

        self.__process()

        self.__container['currencyConverters'].store()
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
        namespace = parser.parse_args()
        return vars(namespace)

    def __readConfig(self) -> any:
        with open(self.__container['config']['config'], 'r') as file:
            return json.load(file)

    def __process(self):
        year = int(self.__container['config']['year'])
        for processor in self.__container['processors']:
            processor.process(year)
