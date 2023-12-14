import argparse
import json
import logging

from .container import container
from .accounting.accountingfactory import AccountingFactory
from .currencyConverters.currencyConverterFactory import CurrencyConverterFactory
from .mergents.mergentFactory import MergentFactory
from .processors.processorFactory import ProcessorFactory
from .transformers.transformerFactory import TransformerFactory


class Application:
    __log = None

    def main(self):
        self.__initializeLogging()

        Application.__log.info('BEGIN')
        container['config'] = self.__parseArguments()
        container['config'] = container['config'] | self.__readConfig()
        container['processors'] = ProcessorFactory.create()
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
        year = int(container['config']['year'])
        for processor in container['processors']:
            processor.process(year)
