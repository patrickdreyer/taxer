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
from ...mergents.payment import Payment
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
        bookings = sorted(bookings, key=lambda b: b[0])
        with open(filePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['Datum', 'Beleg', 'Beschreibung', 'KtSoll', 'KtHaben', 'Betr.Währung', 'Währung', 'Wechselkurs', 'Betrag CHF', 'Anteile', 'KS1', 'Bemerkungen'])
            writer.writerows(booking[1] for booking in bookings)

    def __transform(self, transactions):
        transfers = list()
        self.__transactions = sorted(transactions, key=lambda t: t.dateTime.timestamp())
        for transaction in self.__transactions:
            if issubclass(type(transaction), Trade):
                yield from self.__transformTrade(transaction)
            elif issubclass(type(transaction), Transfer):
                transfers.append(transaction)
            elif isinstance(transaction, Reimbursement):
                yield from self.__transformReimbursement(transaction)
            elif isinstance(transaction, Payment):
                yield from self.__transformPayment(transaction)
            else:
                BananaAccounting.__log.error("Unknown transaction; class='%s'", type(transaction).__name__)
                raise ValueError('Unknown transaction')
        yield from self.__transformTransfers(transfers)

    def __transformTrade(self, transaction):
            date = BananaAccounting.__getDate(transaction)
            cryptoAccount = self.__accounts.get(transaction.cryptoUnit, transaction.mergentId)
            fiatAccount = self.__accounts.get(transaction.fiatUnit, transaction.mergentId)
            fiatExchangeRate = self.__currencyConverters.exchangeRate(transaction.fiatUnit, transaction.dateTime.date())
            cryptoExchangeRate = self.__currencyConverters.exchangeRate(transaction.cryptoUnit, transaction.dateTime.date())
            baseCurrencyFiatAmount = round(transaction.fiatAmount * fiatExchangeRate, 2)
            baseCurrencyFeeAmount = round(transaction.feeAmount * fiatExchangeRate, 2)
            baseCurrencyTotalAmount = baseCurrencyFiatAmount + baseCurrencyFeeAmount
            cryptoCostCenter = '{0}{1}'.format(transaction.cryptoUnit, transaction.mergentId)
            fiatCostCenter = '{0}{1}'.format(transaction.fiatUnit, transaction.mergentId)
            if isinstance(transaction, BuyTrade):
                BananaAccounting.__log.debug("Buy; %s, %s %s", transaction.mergentId, transaction.cryptoAmount, transaction.cryptoUnit)
                description = 'Kauf; {0}'.format(transaction.cryptoUnit)
                # fiat           date,    receipt,        description, debit,                    credit,                   amount,                                         currency,               exchangeRate,       baseCurrencyAmount,      shares, costCenter1
                yield (date[0], [date[1], transaction.id, description, self.__accounts.transfer, fiatAccount,              transaction.fiatAmount + transaction.feeAmount, transaction.fiatUnit,   fiatExchangeRate,   baseCurrencyFiatAmount,  '',     '-'+fiatCostCenter])
                # crypto
                yield (date[0], [date[1], transaction.id, description, cryptoAccount,            self.__accounts.transfer, transaction.cryptoAmount,                       transaction.cryptoUnit, cryptoExchangeRate, baseCurrencyTotalAmount, '',     cryptoCostCenter])
                # fee
                yield (date[0], [date[1], transaction.id, description, self.__accounts.fees,     self.__accounts.transfer, transaction.feeAmount,                          transaction.fiatUnit,   fiatExchangeRate,   baseCurrencyFeeAmount,   '',     ''])
            elif isinstance(transaction, SellTrade):
                BananaAccounting.__log.debug("Sell; %s, %s %s", transaction.mergentId, transaction.cryptoAmount, transaction.cryptoUnit)
                description = 'Verkauf; {0}'.format(transaction.cryptoUnit)
                # crypto         date,    receipt,        description, debit,                    credit,                   amount,                   currency,               exchangeRate,       baseCurrencyAmount,      shares, costCenter1
                yield (date[0], [date[1], transaction.id, description, self.__accounts.transfer, cryptoAccount,            transaction.cryptoAmount, transaction.cryptoUnit, cryptoExchangeRate, baseCurrencyTotalAmount, '',     '-'+cryptoCostCenter])
                # fiat
                yield (date[0], [date[1], transaction.id, description, fiatAccount,              self.__accounts.transfer, transaction.fiatAmount,   transaction.fiatUnit,   fiatExchangeRate,   baseCurrencyFiatAmount,  '',     fiatCostCenter])
                # fee
                yield (date[0], [date[1], transaction.id, description, self.__accounts.fees,     self.__accounts.transfer, transaction.feeAmount,    transaction.fiatUnit,   fiatExchangeRate,   baseCurrencyFeeAmount,   '',     ''])

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
        date = BananaAccounting.__getDate(transaction)
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
                #                date,    receipt,        description,              debit,   credit, amount,             currency,         exchangeRate, baseCurrencyAmount, shares, costCenter1
                yield (date[0], [date[1], transaction.id, 'Transfer von UNBEKANNT', account, '',     transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount, '',     costCenter])
        elif isinstance(transaction, WithdrawTransfer):
            if CurrencyConverters.isFiat(transaction.unit):
                BananaAccounting.__log.debug("Withdraw; %s, %s %s", transaction.mergentId, transaction.amount, transaction.unit)
                #                date,    receipt,        description,  debit,                  credit,  amount,             currency,         exchangeRate, baseCurrencyAmount, shares, costCenter1
                yield (date[0], [date[1], transaction.id, 'Auszahlung', self.__accounts.equity, account, transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount, '',     '-'+costCenter])
            else:
                BananaAccounting.__log.warn("Transfer; %s->???, %s %s", transaction.mergentId, transaction.amount, transaction.unit)
                description = 'Transfer nach UNBEKANNT'
                baseCurrencyFeeAmount = round(transaction.fee * exchangeRate, 2)
                # crypto         date,    receipt,        description, debit,                credit,  amount,             currency,         exchangeRate, baseCurrencyAmount,    shares, costCenter1
                yield (date[0], [date[1], transaction.id, description, '',                   account, transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount,    '',     '-'+costCenter])
                # fee
                yield (date[0], [date[1], '',             description, self.__accounts.fees, account, transaction.fee,    transaction.unit, exchangeRate, baseCurrencyFeeAmount, '',     '-'+costCenter])


    def __transformDoubleTransfers(self, deposit, withdrawal):
        BananaAccounting.__log.debug("Transfer; %s->%s, %s %s", withdrawal.mergentId, deposit.mergentId, deposit.amount, deposit.unit)
        depositDate = BananaAccounting.__getDate(deposit)
        depositDescription = 'Transfer von {0}'.format(withdrawal.mergentId)
        depositAccount = self.__accounts.get(deposit.unit, deposit.mergentId)
        depositCostCenter = '{0}{1}'.format(deposit.unit, deposit.mergentId)
        withdrawalDate = BananaAccounting.__getDate(withdrawal)
        withdrawalDescription = 'Transfer nach {0}'.format(deposit.mergentId)
        withdrawalAccount = self.__accounts.get(withdrawal.unit, withdrawal.mergentId)
        withdrawalCostCenter = '{0}{1}'.format(withdrawal.unit, withdrawal.mergentId)
        exchangeRate = self.__currencyConverters.exchangeRate(deposit.unit, deposit.dateTime.date())
        depositBaseCurrencyAmount = round(deposit.amount * exchangeRate, 2)
        withdrawalBaseCurrencyAmount = round(withdrawal.amount * exchangeRate, 2)
        feeBaseCurrencyAmount = round(withdrawal.fee * exchangeRate, 2)
        # target                   date,              receipt,       description,           deposit,              withdrawal,        amount,            currency,        exchangeRate, baseCurrencyAmount,           shares, costCenter1
        yield (depositDate[0],    [depositDate[1],    deposit.id,    depositDescription,    depositAccount,       '',                deposit.amount,    deposit.unit,    exchangeRate, depositBaseCurrencyAmount,    '',     depositCostCenter])
        # source
        yield (withdrawalDate[0], [withdrawalDate[1], withdrawal.id, withdrawalDescription, '',                   withdrawalAccount, withdrawal.amount, withdrawal.unit, exchangeRate, withdrawalBaseCurrencyAmount, '',     '-'+withdrawalCostCenter])
        # fee
        yield (withdrawalDate[0], [withdrawalDate[1], '',            withdrawalDescription, self.__accounts.fees, withdrawalAccount, withdrawal.fee,    withdrawal.unit, exchangeRate, feeBaseCurrencyAmount,        '',     '-'+withdrawalCostCenter])

    def __transformReimbursement(self, transaction):
        BananaAccounting.__log.debug("Reimbursement; %s, %s %s", transaction.mergentId, transaction.amount, transaction.unit)
        date = BananaAccounting.__getDate(transaction)
        account = self.__accounts.get(transaction.unit, transaction.mergentId)
        exchangeRate = self.__currencyConverters.exchangeRate(transaction.unit, transaction.dateTime.date())
        baseCurrencyAmount = round(transaction.amount * exchangeRate, 2)
        costCenter = '{0}{1}'.format(transaction.unit, transaction.mergentId)
        #                date,    receipt,        description,      deposit, withdrawal,             amount,             currency,         exchangeRate, baseCurrencyAmount, shares, costCenter1
        yield (date[0], [date[1], transaction.id, 'Rückerstattung', account, self.__accounts.equity, transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount, '',     costCenter])

    def __transformPayment(self, transaction):
        BananaAccounting.__log.debug("Payment; %s, %s %s, %s", transaction.mergentId, transaction.amount, transaction.unit, transaction.note)
        date = BananaAccounting.__getDate(transaction)
        account = self.__accounts.get(transaction.unit, transaction.mergentId)
        exchangeRate = self.__currencyConverters.exchangeRate(transaction.unit, transaction.dateTime.date())
        baseCurrencyAmount = round(transaction.amount * exchangeRate, 2)
        costCenter = '{0}{1}'.format(transaction.unit, transaction.mergentId)
        #                date,    receipt,        description, deposit, withdrawal,             amount,             currency,         exchangeRate, baseCurrencyAmount, shares, costCenter1
        yield (date[0], [date[1], transaction.id, 'Bezahlung', account, self.__accounts.equity, transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount, '',     costCenter, transaction.note])

    @staticmethod
    def __getDate(transaction):
        return [transaction.dateTime.date(), transaction.dateTime.date().strftime('%d.%m.%Y')]
