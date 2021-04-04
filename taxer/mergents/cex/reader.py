import csv
import re
from  dateutil import parser

from ..reader import Reader
from ..buyTrade import BuyTrade
from ..sellTrade import SellTrade
from ..withdrawTransfer import WithdrawTransfer
from ..depositTransfer import DepositTransfer


class CexReader(Reader):
    def __init__(self, path=None):
        self.__path = path

    def read(self):
        self.__canceled = list()
        self.__rows = self.readFile()
        try:
            self.nextRowIgnoringCancelations()

            while True:
                if self.__row['Type'] == 'sell':
                    items, id = self.getSameTransactions('sell')
                    date = parser.isoparse(items[0]['DateUTC'])
                    cryptoUnit = items[0]['Symbol']
                    cryptoAmount = abs(float(items[0]['Amount']))
                    fiatUnit = items[1]['Symbol']
                    fiatAmount = sum(abs(float(r['Amount'])) for r in items[1:])
                    feeAmount = sum(float(r['FeeAmount']) for r in items[1:])
                    yield SellTrade('CEX', date, id, cryptoUnit, cryptoAmount, fiatUnit, fiatAmount, feeAmount)
                    continue

                elif self.__row['Type'] == 'buy':                        
                    items, id = self.getSameTransactions('buy')
                    date = parser.isoparse(items[0]['DateUTC'])
                    cryptoUnit = items[0]['Symbol']
                    cryptoAmount = sum(abs(float(r['Amount'])) for r in items[1:])
                    fiatUnit = items[0]['Symbol']
                    fiatAmount = abs(float(items[0]['Amount']))
                    feeAmount = sum(float(r['FeeAmount']) for r in items[1:])
                    yield BuyTrade('CEX', date, id, cryptoUnit, cryptoAmount, fiatUnit, fiatAmount, feeAmount)
                    continue

                elif self.__row['Type'] == 'deposit':
                    date = parser.isoparse(self.__row['DateUTC'])
                    id = re.sub(r'.*\s+([0-9a-f]+)$', r'\1', self.__row['Comment'], 1, flags=re.IGNORECASE)
                    yield DepositTransfer('CEX', date, id, self.__row['Symbol'], float(self.__row['Amount']))

                elif self.__row['Type'] == 'withdraw':
                    date = parser.isoparse(self.__row['DateUTC'])
                    id = re.sub(r'.*\s+([0-9a-f]+)$', r'\1', self.__row['Comment'], 1, flags=re.IGNORECASE)
                    yield WithdrawTransfer('CEX', date, id, self.__row['Symbol'], abs(float(self.__row['Amount'])), 0)

                elif self.__row['Type'] == 'costsNothing':
                    pass

                # cancel and canceled items processed by nextRowIgnoringCancelations()

                self.nextRowIgnoringCancelations()
        except StopIteration:
            pass

    def readFile(self):
        with open(self.__path) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

    def nextRow(self):
        self.__row = next(self.__rows)

    def nextRowIgnoringCancelations(self):
        while True:
            self.nextRow()
            id = self.getId(self.__row)
            if self.__row['Type'] == 'cancel':
                self.__canceled.append(id)
                continue
            if id in self.__canceled:
                continue
            break

    def getId(self, row):
        id = re.sub(r'[^#]+#(\d+)$', r'\1', row['Comment'], 1)
        return id if id != row['Comment'] else None

    # CEX is inconsistent as the item with the order id can come first or last
    # separate logic is used based on if the id is given in the first item or not
    def getSameTransactions(self, type):
        id = self.getId(self.__row)
        return (self.getSameTransactionsIdFirst(type), id) if id else self.getSameTransactionsIdLast(type)

    # keep adding items of the same type until we reach an item with an id actually defining the next block
    def getSameTransactionsIdFirst(self, type):
        transactions = []
        transactions.append(self.__row)
        self.nextRowIgnoringCancelations()
        while self.__row['Type'] == type and not self.getId(self.__row):
            transactions.append(self.__row)
            self.nextRowIgnoringCancelations()
        return transactions

    def getSameTransactionsIdLast(self, type):
        transactions = []
        id = None
        while self.__row['Type'] == type:
            transactions.append(self.__row)
            self.nextRowIgnoringCancelations()
            id = self.getId(self.__row)
            if id:
                transactions.append(self.__row)
                self.nextRowIgnoringCancelations()
                break
        return list(reversed(transactions)), id
