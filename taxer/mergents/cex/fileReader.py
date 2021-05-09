import csv
import itertools
import re
from  dateutil import parser
import pytz

from ..fileReader import FileReader
from ...transactions.buyTrade import BuyTrade
from ...transactions.sellTrade import SellTrade
from ...transactions.withdrawTransfer import WithdrawTransfer
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.reimbursement import Reimbursement


class CexFileReader(FileReader):
    __fileNamePattern = r'.*CEX.*\.csv'

    def __init__(self, path):
        super().__init__(path)

    @property
    def filePattern(self):
        return CexFileReader.__fileNamePattern

    def readFile(self, filePath, year):
        self.__year = year
        self.__canceled = list()
        filteredCancelations = filter(self.__filterCancelations, map(CexFileReader.__convertRow, CexFileReader.__readFile(filePath)))
        filteredYear = filter(self.__filterWrongYear, filteredCancelations)
        sortedType = sorted(filteredYear, key=lambda t:t['Type'])
        groupedByType = itertools.groupby(sortedType, key=lambda t:t['Type'])
        for type, typeGroup in groupedByType:
            for transaction in typeGroup:
                date = transaction['DateUTC']
                id = self.__getId(transaction)
                if type == 'deposit':
                    yield DepositTransfer('CEX', date, id, transaction['Symbol'], float(transaction['Amount']))
                elif type == 'withdraw':
                    yield WithdrawTransfer('CEX', date, id, transaction['Symbol'], abs(float(transaction['Amount'])), 0)
                elif type == 'costsNothing':
                    yield Reimbursement("CEX", date, id, transaction['Symbol'], float(transaction['Amount']))

    @staticmethod
    def __readFile(filePath):
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

    @staticmethod
    def __convertRow(row):
        row['DateUTC'] = pytz.utc.localize(parser.isoparse(row['DateUTC']))
        return row

    def __filterCancelations(self, transaction):
        id = self.__getId(transaction)
        if transaction['Type'] == 'cancel':
            self.__canceled.append(id)
            return False
        if id in self.__canceled:
            return False
        return True

    def __filterWrongYear(self, transaction):
        return transaction['DateUTC'].year == self.__year

    @staticmethod
    def __getId(row):
        id = re.sub(r'[^#]+#(\d+)$', r'\1', row['Comment'], 1)
        return id if id != row['Comment'] else None
