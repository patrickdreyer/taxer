import sys
import logging
import argparse

from .accounting.factory import AccountingFactory
from .mergents.factory import MergentFactory

def main():
    logging.info('Started')
    args = parseArguments()
    readers = MergentFactory().createFromPath(args.input)
    accounting = AccountingFactory().create('Banana')
    process(readers, accounting, args.output)
    logging.info('Stopped')

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Path to the directory containing the platform exports')
    parser.add_argument('output', help='File name to write the output to')
    return parser.parse_args()

def process(readers, accounting, output):
    for reader in readers:
        for transaction in reader.read():
            accounting.transform(transaction)
    accounting.write(output)
