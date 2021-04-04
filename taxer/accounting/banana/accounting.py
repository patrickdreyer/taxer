import logging
import itertools
import csv

from ...mergents.trade import Trade
from ...mergents.buyTrade import BuyTrade
from ...mergents.sellTrade import SellTrade
from ...mergents.transfer import Transfer
from ...mergents.depositTransfer import DepositTransfer
from ...mergents.withdrawTransfer import WithdrawTransfer
from ...mergents.reimbursement import Reimbursement
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
        transfers = list()
        self.__transactions = enumerate(sorted(transactions, key=lambda t: t.dateTime.timestamp()))
        try:
            self.__nextTransaction()
            while True:
                if issubclass(type(self.__transaction), Trade):
                    yield from self.__transformTrade()
                    self.__nextTransaction()
                elif issubclass(type(self.__transaction), Transfer):
                    transfers.append(self.__transaction)
                    self.__nextTransaction()
                elif isinstance(self.__transaction, Reimbursement):
                    yield from self.__transformReimbursement()
                    self.__nextTransaction()
                else:
                    BananaAccounting.__log.error("Unknown transaction; class='%s'", type(self.__transaction).__name__)
                    raise ValueError('Unknown transaction')
        except StopIteration:
            pass
        finally:
            yield from self.__transformTransfers(transfers)

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
                BananaAccounting.__log.debug("Buy; %s, %s %s", self.__transaction.mergentId, self.__transaction.cryptoAmount, self.__transaction.cryptoUnit)
                description = 'Kauf; {0}'.format(self.__transaction.cryptoUnit)
                # fiat           date,    receipt,               description, debit,                    credit,                   amount,                                                       currency,                      exchangeRate,       baseCurrencyAmount,       shares, costCenter1
                yield (date[0], [date[1], self.__transaction.id, description, self.__accounts.transfer, fiatAccount,              self.__transaction.fiatAmount + self.__transaction.feeAmount, self.__transaction.fiatUnit,   fiatExchangeRate,   baseCurrencyFiatAmount,   '',     '-'+fiatCostCenter])
                # crypto
                yield (date[0], [date[1], self.__transaction.id, description, cryptoAccount,            self.__accounts.transfer, -self.__transaction.cryptoAmount,                             self.__transaction.cryptoUnit, cryptoExchangeRate, -baseCurrencyTotalAmount, '',     cryptoCostCenter])
                # fee
                yield (date[0], [date[1], self.__transaction.id, description, self.__accounts.fees,     self.__accounts.transfer, -self.__transaction.feeAmount,                                self.__transaction.fiatUnit,   fiatExchangeRate,   -baseCurrencyFeeAmount,   '',     ''])
            elif isinstance(self.__transaction, SellTrade):
                BananaAccounting.__log.debug("Sell; %s, %s %s", self.__transaction.mergentId, self.__transaction.cryptoAmount, self.__transaction.cryptoUnit)
                description = 'Verkauf; {0}'.format(self.__transaction.cryptoUnit)
                # cryp           date,    receipt,               description, debit,                    credit,                   amount,                          currency,                      exchangeRate,       baseCurrencyAmount,      shares, costCenter1
                yield (date[0], [date[1], self.__transaction.id, description, self.__accounts.transfer, cryptoAccount,            self.__transaction.cryptoAmount, self.__transaction.cryptoUnit, cryptoExchangeRate, baseCurrencyTotalAmount, '',     '-'+cryptoCostCenter])
                # fiat
                yield (date[0], [date[1], self.__transaction.id, description, fiatAccount,              self.__accounts.transfer, -self.__transaction.fiatAmount,  self.__transaction.fiatUnit,   fiatExchangeRate,   -baseCurrencyFiatAmount, '',     fiatCostCenter])
                # fee
                yield (date[0], [date[1], self.__transaction.id, description, self.__accounts.fees,     self.__accounts.transfer, -self.__transaction.feeAmount,   self.__transaction.fiatUnit,   fiatExchangeRate,   -baseCurrencyFeeAmount,  '',     ''])

    def __transformTransfers(self, transfers):
        deposits = [transfer for transfer in transfers if isinstance(transfer, DepositTransfer)]
        withdrawals = [transfer for transfer in transfers if isinstance(transfer, WithdrawTransfer)]
        for deposit in deposits:
            matches = [withdrawal for withdrawal in withdrawals if withdrawal.mergentId != deposit.mergentId and withdrawal.amount == deposit.amount]
            if len(matches) == 0:
                yield from self.__transformSingleTransfer(deposit)
            elif len(matches) == 1:
                yield from self.__transformDoubleTransfers(deposit, matches[0])
                withdrawals.remove(matches[0])
            else:
                BananaAccounting.__log.error("Multiple matching transfers; %s, %s", deposit, matches)
                raise ValueError('Multiple matching transfers')
        for withdrawal in withdrawals:
            yield from self.__transformSingleTransfer(withdrawal)

    def __transformSingleTransfer(self, transaction):
        date = BananaAccounting.getDate(transaction)
        account = self.__accounts.get(transaction.unit, transaction.mergentId)
        exchangeRate = self.__currencyConverters.exchangeRate(transaction.unit, transaction.dateTime.date())
        baseCurrencyAmount = round(transaction.amount * exchangeRate, 2)
        costCenter = '{0}{1}'.format(transaction.unit, transaction.mergentId)
        if isinstance(transaction, DepositTransfer):
            if CurrencyConverters.isFiat(transaction.unit):
                BananaAccounting.__log.debug("Deposit; %s, %s %s", transaction.mergentId, transaction.amount, transaction.unit)
                #                date,    receipt,        description,  debit,   credit,                 amount,             currency,         exchangeRate, baseCurrencyAmount, shares, costCenter1
                yield (date[0], [date[1], transaction.id, 'Einzahlung', account, self.__accounts.equity, transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount, '',     costCenter])
            else:
                BananaAccounting.__log.warn("Transfer; ???->%s, %s %s", transaction.mergentId, transaction.amount, transaction.unit)
                #                date,    receipt,        description,          debit,   credit, amount,             currency,         exchangeRate, baseCurrencyAmount, shares, costCenter1
                yield (date[0], [date[1], transaction.id, 'Transfer',           account, '',     transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount, '',     costCenter])
                yield (date[0], [date[1], '',             'HERKUNFT UNBEKANNT', '',      '',     '',                 '',               '',           '',                 '',     ''])
        elif isinstance(transaction, WithdrawTransfer):
            if CurrencyConverters.isFiat(transaction.unit):
                BananaAccounting.__log.debug("Withdraw; %s, %s %s", transaction.mergentId, transaction.amount, transaction.unit)
                #                date,    receipt,        description,  debit,                  credit,  amount,              currency,         exchangeRate, baseCurrencyAmount, shares, costCenter1
                yield (date[0], [date[1], transaction.id, 'Auszahlung', self.__accounts.equity, account, -transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount, '',     '-'+costCenter])
            else:
                BananaAccounting.__log.warn("Transfer; %s->???, %s %s", transaction.mergentId, transaction.amount, transaction.unit)
                #                date,    receipt,        description,       debit, credit,  amount,              currency,         exchangeRate, baseCurrencyAmount,  shares, costCenter1
                yield (date[0], [date[1], '',             'ZIEL UNBEGKANNT', '',    '',      '',                  '',               '',           '',                  '',     ''])
                yield (date[0], [date[1], transaction.id, 'Transfer',        '',    account, -transaction.amount, transaction.unit, exchangeRate, -baseCurrencyAmount, '',     '-'+costCenter])

    def __transformDoubleTransfers(self, deposit, withdrawal):
        BananaAccounting.__log.debug("Transfer; %s->%s, %s %s", withdrawal.mergentId, deposit.mergentId, deposit.amount, deposit.unit)
        depositDate = BananaAccounting.getDate(deposit)
        depositDescription = 'Transfer from {0}'.format(deposit.mergentId)
        depositAccount = self.__accounts.get(deposit.unit, deposit.mergentId)
        depositCostCenter = '{0}{1}'.format(deposit.unit, deposit.mergentId)
        withdrawalDate = BananaAccounting.getDate(withdrawal)
        withdrawalDescription = 'Transfer to {0}'.format(deposit.mergentId)
        withdrawalAccount = self.__accounts.get(withdrawal.unit, withdrawal.mergentId)
        withdrawalCostCenter = '{0}{1}'.format(withdrawal.unit, withdrawal.mergentId)
        exchangeRate = self.__currencyConverters.exchangeRate(deposit.unit, deposit.dateTime.date())
        depositBaseCurrencyAmount = round(deposit.amount * exchangeRate, 2)
        withdrawalBaseCurrencyAmount = round(withdrawal.amount * exchangeRate, 2)
        #                          date,              receipt,       description,           deposit,        withdrawal,         amount,             currency,        exchangeRate, baseCurrencyAmount,            shares, costCenter1
        yield (depositDate[0],    [depositDate[1],    deposit.id,    depositDescription,    depositAccount, '',                 deposit.amount,     deposit.unit,    exchangeRate, depositBaseCurrencyAmount,     '',     depositCostCenter])
        yield (withdrawalDate[0], [withdrawalDate[1], withdrawal.id, withdrawalDescription, '',              withdrawalAccount, -withdrawal.amount, withdrawal.unit, exchangeRate, -withdrawalBaseCurrencyAmount, '',     '-'+withdrawalCostCenter])

    def __transformReimbursement(self):
        BananaAccounting.__log.debug("Reimbursement; %s, %s %s", self.__transaction.mergentId, self.__transaction.amount, self.__transaction.unit)
        date = BananaAccounting.getDate(self.__transaction)
        account = self.__accounts.get(self.__transaction.unit, self.__transaction.mergentId)
        exchangeRate = self.__currencyConverters.exchangeRate(self.__transaction.unit, self.__transaction.dateTime.date())
        baseCurrencyAmount = round(self.__transaction.amount * exchangeRate, 2)
        costCenter = '{0}{1}'.format(self.__transaction.unit, self.__transaction.mergentId)
        #                date,    receipt,               description,      deposit, withdrawal,             amount,                    currency,                exchangeRate, baseCurrencyAmount, shares, costCenter1
        yield (date[0], [date[1], self.__transaction.id, 'Rückerstattung', account, self.__accounts.equity, self.__transaction.amount, self.__transaction.unit, exchangeRate, baseCurrencyAmount, '',     costCenter])

    @staticmethod
    def getDate(transaction):
        return [transaction.dateTime.date(), transaction.dateTime.date().strftime('%d.%m.%Y')]
