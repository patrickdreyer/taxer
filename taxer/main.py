import sys
import logging
import argparse

from .accounting.factory import AccountingFactory
from .mergents.factory import MergentFactory
from .writers.factory import WriterFactory

def main():
    logging.info('Started')
    args = parseArguments()
    readers = MergentFactory().createFromPath(args.input)
    accounting = AccountingFactory().create('Banana')
    transformer = accounting.createTransformer()
    writer = WriterFactory().create('csv')
    process(readers, transformer, writer)
    logging.info('Stopped')

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Path to the directory containing the platform exports')
    parser.add_argument('output', help='File name to write the output to')
    return parser.parse_args()

def process(readers, transformer, writer):
    for reader in readers:
        for mergentTransaction in reader.read():
            accountingTransactions = transformer.transform(mergentTransaction)
            writer.write(accountingTransactions)
