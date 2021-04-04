import logging
import itertools
import csv

from ...mergents.trade import Trade
from ...mergents.buyTrade import BuyTrade
from ...mergents.sellTrade import SellTrade
from ...mergents.transfer import Transfer
from ...mergents.depositTransfer import DepositTransfer
from ...mergents.withdrawTransfer import WithdrawTransfer
from ...currencyConverters.currencyConverters import CurrencyConverters
from ..accounting import Accounting
from .accounts import BananaAccounts


class BananaAccounting(Accounting):
    __log = logging.getLogger(__name__)

    def __init__(self, currencyConverters):
        self.__accounts = BananaAccounts()
        self.__currencyConverters = currencyConverters

    def write(self, transactions, filePath):
        bookings = self.__transform(transactions)
        with open(filePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['date', 'receipt', 'description', 'debit', 'credit', 'amount', 'currency', 'exchangeRate', 'baseCurrencyAmount', 'shares', 'costCenter1'])
            writer.writerows(booking[1] for booking in bookings)

    def __transform(self, transactions):
        self.__transactions = enumerate(sorted(transactions, key=lambda t: t.dateTime.timestamp()))
        try:
            self.__nextTransaction()
            while True:
                if issubclass(type(self.__transaction), Trade):
                    yield from self.__transformTrade()
                    self.__nextTransaction()
                elif issubclass(type(self.__transaction), Transfer):
                    yield from self.__transformContiguousTransfers()
                else:
                    BananaAccounting.__log.error("Unknown transaction; class='%s'", type(self.__transaction).__name__)
        except StopIteration:
            pass

    def __nextTransaction(self):
        self.__transaction = next(self.__transactions)[1]

    def __transformTrade(self):
            date = BananaAccounting.getDate(self.__transaction)
            cryptoAccount = self.__accounts.get(self.__transaction.cryptoUnit, self.__transaction.mergentId)
            fiatAccount = self.__accounts.get(self.__transaction.fiatUnit, self.__transaction.mergentId)
            fiatExchangeRate = self.__currencyConverters.exchangeRate(self.__transaction.fiatUnit, self.__transaction.dateTime.date())
            cryptoExchangeRate = self.__currencyConverters.exchangeRate(self.__transaction.cryptoUnit, self.__transaction.dateTime.date())
            baseCurrencyFiatAmount = round(self.__transaction.fiatAmount * fiatExchangeRate, 2)
            baseCurrencyFeeAmount = round(self.__transaction.feeAmount * fiatExchangeRate, 2)
            baseCurrencyTotalAmount = baseCurrencyFiatAmount + baseCurrencyFeeAmount
            cryptoCostCenter = '{0}{1}'.format(self.__transaction.cryptoUnit, self.__transaction.mergentId)
            fiatCostCenter = '{0}{1}'.format(self.__transaction.fiatUnit, self.__transaction.mergentId)
            if isinstance(self.__transaction, BuyTrade):
                BananaAccounting.__log.debug("Buy %s %s", self.__transaction.cryptoAmount, self.__transaction.cryptoUnit)
                description = 'Kauf; {0}'.format(self.__transaction.cryptoUnit)
                # fiat           date,    receipt,               description, debit,                    credit,                   amount,                                                       currency,                      exchangeRate,       baseCurrencyAmount,      shares, costCenter1
                yield (date[0], [date[1], self.__transaction.id, description, self.__accounts.transfer, fiatAccount,              self.__transaction.fiatAmount + self.__transaction.feeAmount, self.__transaction.fiatUnit,   fiatExchangeRate,   baseCurrencyFiatAmount,  '',     '-'+fiatCostCenter])
                # crypto
                yield (date[0], [date[1], self.__transaction.id, description, cryptoAccount,            self.__accounts.transfer, self.__transaction.cryptoAmount,                              self.__transaction.cryptoUnit, cryptoExchangeRate, baseCurrencyTotalAmount, '',     cryptoCostCenter])
                # fee
                yield (date[0], [date[1], self.__transaction.id, description, self.__accounts.fees,     self.__accounts.transfer, self.__transaction.feeAmount,                                 self.__transaction.fiatUnit,   fiatExchangeRate,   baseCurrencyFeeAmount,   '',     ''])
            elif isinstance(self.__transaction, SellTrade):
                BananaAccounting.__log.debug("Sell %s %s", self.__transaction.cryptoAmount, self.__transaction.cryptoUnit)
                description = 'Verkauf; {0}'.format(self.__transaction.cryptoUnit)
                # cryp           date,    receipt,               description, debit,                    credit,                   amount,                          currency,                      exchangeRate,       baseCurrencyAmount,      shares, costCenter1
                yield (date[0], [date[1], self.__transaction.id, description, self.__accounts.transfer, cryptoAccount,            self.__transaction.cryptoAmount, self.__transaction.cryptoUnit, cryptoExchangeRate, baseCurrencyTotalAmount, '',     '-'+cryptoCostCenter])
                # fiat
                yield (date[0], [date[1], self.__transaction.id, description, fiatAccount,              self.__accounts.transfer, self.__transaction.fiatAmount,   self.__transaction.fiatUnit,   fiatExchangeRate,   baseCurrencyFiatAmount,  '',     fiatCostCenter])
                # fee
                yield (date[0], [date[1], self.__transaction.id, description, self.__accounts.fees,     self.__accounts.transfer, self.__transaction.feeAmount,    self.__transaction.fiatUnit,   fiatExchangeRate,   baseCurrencyFeeAmount,   '',     ''])

    def __transformContiguousTransfers(self):
        # get all contiguous transfers
        transfers = list()
        while isinstance(self.__transaction, Transfer):
            transfers.append(self.__transaction)
            self.__nextTransaction()

        # group by amount to group matching transfers; always sorted before groupby
        transfers = sorted(transfers, key=lambda group: abs(group.amount))
        for _, group in itertools.groupby(transfers, key=lambda t: abs(t.amount)):
            group = list(group)
            if len(group) == 1:
                yield from self.__transformSingleTransfer(group[0])
            elif len(group) == 2:
                yield from self.__transformDoubleTransfers(group)
            else:
                BananaAccounting.__log.error("More than two matching transfers; transfers='%s'", group)
                raise ValueError()

    def __transformSingleTransfer(self, transaction):
        date = BananaAccounting.getDate(transaction)
        account = self.__accounts.get(transaction.unit, transaction.mergentId)
        exchangeRate = self.__currencyConverters.exchangeRate(transaction.unit, transaction.dateTime.date())
        baseCurrencyAmount = round(transaction.amount * exchangeRate, 2)
        costCenter = '{0}{1}'.format(transaction.unit, transaction.mergentId)
        if isinstance(transaction, DepositTransfer):
            if CurrencyConverters.isFiat(transaction.unit):
                BananaAccounting.__log.debug("Deposit %s %s", transaction.amount, transaction.unit)
                #                date,    receipt,        description,  debit,   credit,                 amount,             currency,         exchangeRate, baseCurrencyAmount, shares, costCenter1
                yield (date[0], [date[1], transaction.id, 'Einzahlung', account, self.__accounts.equity, transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount, '',     costCenter])
            else:
                BananaAccounting.__log.warn("Transfer %s %s", transaction.amount, transaction.unit)
                #                date,    receipt,        description,          debit,   credit, amount,             currency,         exchangeRate, baseCurrencyAmount, shares, costCenter1
                yield (date[0], [date[1], transaction.id, 'Transfer',           account, '',     transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount, '',     costCenter])
                yield (date[0], [date[1], '',             'HERKUNFT UNBEKANNT', '',      '',     '',                 '',               '',           '',                 '',     ''])
        elif isinstance(transaction, WithdrawTransfer):
            if CurrencyConverters.isFiat(transaction.unit):
                BananaAccounting.__log.debug("Withdraw %s %s", transaction.amount, transaction.unit)
                #                date,    receipt,        description,  debit,                  credit,  amount,             currency,         exchangeRate, baseCurrencyAmount, shares, costCenter1
                yield (date[0], [date[1], transaction.id, 'Auszahlung', self.__accounts.equity, account, transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount, '',     '-'+costCenter])
            else:
                BananaAccounting.__log.warn("Transfer %s %s", transaction.amount, transaction.unit)
                #                date,    receipt,        description,      debit, credit,  amount,             currency,         exchangeRate, baseCurrencyAmount, shares, costCenter1
                yield (date[0], [date[1], '',             'ZIEL UNBEGKANNT', '',    '',      '',                 '',               '',           '',                 '',     ''])
                yield (date[0], [date[1], transaction.id, 'Transfer',       '',    account, transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount, '',     '-'+costCenter])

    def __transformDoubleTransfers(self, transactions):
        debit = [transaction for transaction in transactions if isinstance(transaction, DepositTransfer)][0]
        credit = [transaction for transaction in transactions if isinstance(transaction, WithdrawTransfer)][0]
        debitDate = BananaAccounting.getDate(debit)
        debitDescription = 'Transfer from {0}'.format(credit.mergentId)
        debitAccount = self.__accounts.get(debit.unit, debit.mergentId)
        debitCostCenter = '{0}{1}'.format(debit.unit, debit.mergentId)
        creditDate = BananaAccounting.getDate(credit)
        creditDescription = 'Transfer to {0}'.format(debit.mergentId)
        creditAccount = self.__accounts.get(credit.unit, credit.mergentId)
        creditCostCenter = '{0}{1}'.format(credit.unit, credit.mergentId)
        exchangeRate = self.__currencyConverters.exchangeRate(debit.unit, debit.dateTime.date())
        baseCurrencyAmount = round(debit.amount * exchangeRate, 2)
        #                      date,          receipt,   description,       debit,        credit,        amount,        currency,    exchangeRate, baseCurrencyAmount, shares, costCenter1
        yield (debitDate[0],  [debitDate[1],  debit.id,  debitDescription,  debitAccount, '',            debit.amount,  debit.unit,  exchangeRate, baseCurrencyAmount, '',     debitCostCenter])
        yield (creditDate[0], [creditDate[1], credit.id, creditDescription, '',           creditAccount, credit.amount, credit.unit, exchangeRate, baseCurrencyAmount, '',     '-'+creditCostCenter])

    @staticmethod
    def getDate(transaction):
        return [transaction.dateTime.date(), transaction.dateTime.date().strftime('%d.%m.%Y')]
