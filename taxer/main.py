import sys
import logging
import argparse

from .mergents.factory import MergentFactory
from .currencyConverters.currencyConverter import CurrencyConverter
from .accounting.factory import AccountingFactory


def main():
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M',
        filename='taxer.log', filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)  

    log.info('Started')
    args = parseArguments()
    readers = MergentFactory().createFromPath(args.input)
    currencyConverter = CurrencyConverter(args.input)
    accounting = AccountingFactory(currencyConverter).create('Banana')
    process(readers, accounting, args.output)
    log.info('Stopped')

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Path to the directory containing the platform exports')
    parser.add_argument('output', help='File name to write the output to')
    return parser.parse_args()

def process(readers, accounting, output):
    unsortedTransactions = reading(readers)
    sortedTransactions = sorted(unsortedTransactions, key=lambda t: t.dateTime.timestamp())
    for transaction in sortedTransactions:
        accounting.transform(transaction)
    accounting.write(output)

def reading(readers):
    for reader in readers:
        yield from reader.read()
