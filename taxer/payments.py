import os
import csv

from .mergents.withdrawTransfer import WithdrawTransfer
from .mergents.payment import Payment


class Payments:
    __fileName = 'Payments.csv'

    def __init__(self, path):
        self.__path = path

    def transform(self, transactions):
        self.__loadPayments()
        return map(self.__map, transactions)

    def __loadPayments(self):
        filePath = os.path.join(self.__path, Payments.__fileName)
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            self.__payments = {row['id']:row['comment'] for row in reader}

    def __map(self, transaction):
        if not isinstance(transaction, WithdrawTransfer):
            return transaction
        if not transaction.id in self.__payments:
            return transaction
        return Payment(transaction, self.__payments[transaction.id])
