import csv
import re
from  dateutil import parser

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

    def readFile(self, filePath):
        self.__canceled = list()
        self.__partialSell = {'id': None, 'fiat': None, 'crypto': list()}
        self.__partialBuy = {'id': None, 'fiat': None, 'crypto': list()}
        self.__rows = self.__readFile(filePath)
        try:
            self.__nextRowIgnoringCancelations()
            while True:
                id = CexFileReader.__getId(self.__row)
                if self.__row['Type'] == 'sell':
                    if not id:
                        self.__partialSell['crypto'].append(self.__row)
                    elif not self.__partialSell['id']:
                        self.__partialSell[id] = id
                        self.__partialSell['fiat'] = self.__row
                    else:
                        date = parser.isoparse(self.__partialSell['fiat']['DateUTC'])
                        cryptoUnit = self.__partialSell['crypto'][0]['Symbol']
                        cryptoAmount = abs(float(self.__partialSell['fiat']['Amount']))
                        fiatUnit = self.__partialSell['fiat']['Symbol']
                        fiatAmount = sum(abs(float(r['Amount'])) for r in self.__partialSell['crypto'])
                        feeAmount = sum(float(r['FeeAmount']) for r in self.__partialSell['crypto'])
                        yield SellTrade('CEX', date, id, cryptoUnit, cryptoAmount, fiatUnit, fiatAmount, feeAmount)
                        self.__partialSell = {'id': id, 'fiat': self.__row, 'crypto': list()}

                elif self.__row['Type'] == 'buy':                        
                    if not id:
                        self.__partialBuy['crypto'].append(self.__row)
                    elif not self.__partialBuy['id']:
                        self.__partialBuy['id'] = id
                        self.__partialBuy['fiat'] = self.__row
                    else:
                        date = parser.isoparse(self.__partialBuy['fiat']['DateUTC'])
                        if len(self.__partialBuy['crypto']) > 0:
                            cryptoUnit = self.__partialBuy['crypto'][0]['Symbol']
                            cryptoAmount = sum(abs(float(r['Amount'])) for r in self.__partialBuy['crypto'])
                        else:
                            cryptoUnit = ''
                            cryptoAmount = 0
                        fiatUnit = self.__partialBuy['fiat']['Symbol']
                        fiatAmount = abs(float(self.__partialBuy['fiat']['Amount']))
                        feeAmount = sum(float(r['FeeAmount']) for r in self.__partialBuy['crypto'])
                        yield BuyTrade('CEX', date, id, cryptoUnit, cryptoAmount, fiatUnit, fiatAmount, feeAmount)
                        self.__partialBuy = {'id': id, 'fiat': self.__row, 'crypto': list()}

                elif self.__row['Type'] == 'deposit':
                    date = parser.isoparse(self.__row['DateUTC'])
                    yield DepositTransfer('CEX', date, id, self.__row['Symbol'], float(self.__row['Amount']))

                elif self.__row['Type'] == 'withdraw':
                    date = parser.isoparse(self.__row['DateUTC'])
                    yield WithdrawTransfer('CEX', date, id, self.__row['Symbol'], abs(float(self.__row['Amount'])), 0)

                elif self.__row['Type'] == 'costsNothing':
                    # looks like costsNothing is like canceled as related fiat transaction has no crypto transactions
                    self.__canceled.append(id)
                    date = parser.isoparse(self.__row['DateUTC'])
                    yield Reimbursement("CEX", date, id, self.__row['Symbol'], float(self.__row['Amount']))

                # cancel and canceled items processed by nextRowIgnoringCancelations()

                self.__nextRowIgnoringCancelations()
        except StopIteration:
            pass

    def __readFile(self, filePath):
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

    def __nextRow(self):
        self.__row = next(self.__rows)

    def __nextRowIgnoringCancelations(self):
        while True:
            self.__nextRow()
            id = self.__getId(self.__row)
            if self.__row['Type'] == 'cancel':
                self.__canceled.append(id)
                continue
            if id in self.__canceled:
                continue
            break

    @staticmethod
    def __getId(row):
        id = re.sub(r'[^#]+#(\d+)$', r'\1', row['Comment'], 1)
        return id if id != row['Comment'] else None
