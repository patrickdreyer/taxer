import logging
import os
import pickle

from ..container import Container


class TransactionsProcessor:
    __log = logging.getLogger(__name__)
    __fileName = 'transactions.json'

    def __init__(self, container:Container):
        self.__container = container

    def process(self, year):
        transactions = self.__deserialize()
        if transactions == None:
            transactions = (t for t in self.__read(year) if t != None)
            transactions = sorted(transactions, key=lambda t: t.dateTime)
            self.__serialize(transactions)
        for accounting in self.__container['accountings']:
            transactions = list(self.__transform(transactions))
            accounting.write(transactions)

    def __read(self, year):
        readers = self.__container['mergentReaders']
        for reader in readers:
            yield from reader.read(year)

    def __transform(self, transactions):
        for transformer in self.__container['transformers']:
            transactions = transformer.transform(transactions)
        return transactions

    def __serialize(self, transactions):
        if not self.__container['config']['transactions']:
            return
        TransactionsProcessor.__log.info("Serialize transactions; filePath='%s'", self.__container['config']['transactions'])
        if not os.path.exists(self.__container['config']['transactions']):
            os.makedirs(self.__container['config']['transactions'])
        with open(os.path.join(self.__container['config']['transactions'], TransactionsProcessor.__fileName), 'wb') as file:
            pickle.dump(transactions, file)

    def __deserialize(self):
        if not self.__container['config']['transactions']:
            return None
        filePath = os.path.join(self.__container['config']['transactions'], TransactionsProcessor.__fileName)
        if not os.path.isfile(filePath):
            return None
        TransactionsProcessor.__log.info("Deserialize transactions; filePath='%s'", filePath)
        with open(filePath, 'rb') as file:
            return pickle.load(file)
