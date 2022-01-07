import logging
import itertools
import csv
import os
import datetime
from  dateutil import parser

from ..accounting import Accounting
from ...currencyConverters.currencyConverters import CurrencyConverters
from ...transactions.trade import Trade
from ...transactions.buyTrade import BuyTrade
from ...transactions.sellTrade import SellTrade
from ...transactions.marginTrade import MarginTrade
from ...transactions.transfer import Transfer
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.withdrawTransfer import WithdrawTransfer
from ...transactions.reimbursement import Reimbursement
from ...transactions.payment import Payment
from ...transactions.covesting import Covesting
from ...transactions.enterLobby import EnterLobby
from ...transactions.exitLobby import ExitLobby
from ...transactions.startStake import StartStake
from ...transactions.endStake import EndStake


class ShareholderAccounting(Accounting):
    __shareholderFileName = 'Shareholder.csv'
    __accountsOutputFileName = 'Accounts.csv'

    __log = logging.getLogger(__name__)

    def __init__(self, input, output, year, config, currencyConverters):
        self.__mergents = dict()
        self.__input = input
        self.__output = output
        self.__year = year
        self.__currencyConverters = currencyConverters

    def write(self, transactions):
        self.__readShareholder()
        self.__createAccounts()
        self.__processTransactions(transactions)
        self.__writeShareholder()
        self.__writeAccounts()

    def __createAccounts(self):
        firstDayOfYear = datetime.datetime(int(self.__year), 1, 1)
        openings = [shareholder for shareholder in self.__shareholder if shareholder['DateTime'] == firstDayOfYear]
        for opening in openings:
            self.__createAccount(opening['Mergent'], opening['Currency'], opening['Shareholder'], float(opening['Amount']))

    def __readShareholder(self):
        filePath = os.path.join(self.__input, ShareholderAccounting.__shareholderFileName)
        with open(filePath) as csvFile:
            self.__shareholder = csv.DictReader(csvFile, delimiter=',')
            self.__shareholder = map(ShareholderAccounting.__transformShareholder, self.__shareholder)
            self.__shareholder = sorted(self.__shareholder, key=lambda s:s['DateTime'])

    def __processTransactions(self, transactions):
        shareholder = [shareholder for shareholder in self.__shareholder if shareholder['DateTime'] > firstDayOfYear]
        for transaction in transactions:
            if isinstance(transaction, BuyTrade):
                self.__changeAccount(transaction.mergentId, transaction.cryptoUnit, transaction.cryptoAmount)
                self.__changeAccount(transaction.mergentId, transaction.fiatUnit, -transaction.fiatAmount)
                self.__changeAccount(transaction.mergentId, transaction.fiatUnit, -transaction.feeAmount)
            elif isinstance(transaction, SellTrade):
                self.__changeAccount(transaction.mergentId, transaction.cryptoUnit, -transaction.cryptoAmount)
                self.__changeAccount(transaction.mergentId, transaction.fiatUnit, transaction.fiatAmount)
                self.__changeAccount(transaction.mergentId, transaction.fiatUnit, -transaction.feeAmount)
            elif isinstance(transaction, DepositTransfer):
                self.__changeAccount(transaction.mergentId, transaction.unit, transaction.amount)
            elif isinstance(transaction, WithdrawTransfer):
                self.__changeAccount(transaction.mergentId, transaction.unit, -transaction.amount)
            elif isinstance(transaction, Reimbursement):
                self.__changeAccount(transaction.mergentId, transaction.unit, transaction.amount)
            elif isinstance(transaction, Payment):
                self.__changeAccount(transaction.mergentId, transaction.unit, -transaction.amount)
            elif isinstance(transaction, Covesting):
                pass
            elif isinstance(transaction, EnterLobby):
                pass
            elif isinstance(transaction, ExitLobby):
                pass
            elif isinstance(transaction, StartStake):
                pass
            elif isinstance(transaction, EndStake):
                pass

    def __writeShareholder(self):
        lastDayOfYear = datetime.datetime(int(self.__year), 12, 31).strftime('%d-%m-%Y')
        outputFilePath = os.path.join(self.__output, ShareholderAccounting.__shareholderFileName)
        with open(outputFilePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['Shareholder', 'DateTime', 'Mergent', 'Currency', 'Amount', 'Percentage'])
            for mergent, accounts in self.__mergents.items():
                for account, shareholders in accounts.items():
                    for shareholder, values in shareholders.items():
                        writer.writerow([shareholder, lastDayOfYear, mergent, account, values[0], 100 * values[1]])

    def __writeAccounts(self):
        outputFilePath = os.path.join(self.__output, ShareholderAccounting.__accountsOutputFileName)
        with open(outputFilePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['Mergent', 'Currency', 'Shareholder', 'Amount', 'Percentage'])
            for mergent, accounts in self.__mergents.items():
                for account, shareholders in accounts.items():
                    total = sum([value[0] for value in shareholders.values()])
                    writer.writerow([mergent, account, '', total, 100])
                    for shareholder, values in shareholders.items():
                        writer.writerow([mergent, account, shareholder, values[0], 100 * values[1]])

    def __createAccount(self, mergentId, account, shareholder, amount):
        if not mergentId in self.__mergents:
            self.__mergents[mergentId] = dict()
        if not account in self.__mergents[mergentId]:
            self.__mergents[mergentId][account] = dict()
        shareholders = self.__mergents[mergentId][account]
        if not shareholder in shareholders:
            shareholders[shareholder] = [0.0, 0.0]
        shareholders[shareholder][0] = shareholders[shareholder][0] + amount
        total = sum([float(value[0]) for value in shareholders.values()])
        for shareholder in shareholders.values():
            shareholder[1] = shareholder[0] / total if total > 0 else 1.0

    def __changeAccount(self, mergentId, account, amount):
        ShareholderAccounting.__log.debug("Account change; %s, %s %s", mergentId, account, amount)
        if not mergentId in self.__mergents:
            raise KeyError("Unknown mergent; mergentId='{}', account='{}".format(mergentId, account))
        if not account in self.__mergents[mergentId]:
            raise KeyError("Unknown account; mergentId='{}', account='{}".format(mergentId, account))
        shareholders = self.__mergents[mergentId][account]
        if len(shareholders) == 0:
            raise Exception("No sharesholders; mergentId='{}', account='{}".format(mergentId, account))
        total = sum([value[0] for value in shareholders.values()]) + amount
        for shareholder in shareholders.values():
            shareholder[0] = total * shareholder[1]

    @staticmethod
    def __transformShareholder(shareholder):
        shareholder['DateTime'] = parser.parse(shareholder['DateTime'])
        return shareholder
