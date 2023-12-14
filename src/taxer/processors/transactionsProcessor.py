import logging
import os
import pickle

from ..container import container


class TransactionsProcessor:
    __log = logging.getLogger(__name__)
    __fileName = 'transactions.json'

    def process(self, year):
        transactions = self.__deserialize()
        if transactions == None:
            transactions = (t for t in self.__read(year) if t != None)
            transactions = sorted(transactions, key=lambda t: t.dateTime)
            self.__serialize(transactions)
        for accounting in container['accountings']:
            transactions = list(self.__transform(transactions))
            accounting.write(transactions)

    def __read(self, year):
        readers = container['mergentReaders']
        for reader in readers:
            yield from reader.read(year)

    def __transform(self, transactions):
        for transformer in container['transformers']:
            transactions = transformer.transform(transactions)
        return transactions

    def __serialize(self, transactions):
        if not container['config']['transactions']:
            return
        TransactionsProcessor.__log.info("Serialize transactions; filePath='%s'", container['config']['transactions'])
        if not os.path.exists(container['config']['transactions']):
            os.makedirs(container['config']['transactions'])
        with open(os.path.join(container['config']['transactions'], TransactionsProcessor.__fileName), 'wb') as file:
            pickle.dump(transactions, file)

    def __deserialize(self):
        if not container['config']['transactions']:
            return None
        filePath = os.path.join(container['config']['transactions'], TransactionsProcessor.__fileName)
        if not os.path.isfile(filePath):
            return None
        TransactionsProcessor.__log.info("Deserialize transactions; filePath='%s'", filePath)
        with open(filePath, 'rb') as file:
            return pickle.load(file)
