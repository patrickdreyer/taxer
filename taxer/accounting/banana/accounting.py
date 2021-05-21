import logging
import itertools
import csv
import os

from .accounts import BananaAccounts
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


class BananaAccounting(Accounting):
    __fileName = 'banana.csv'

    __log = logging.getLogger(__name__)

    def __init__(self, output, config, currencyConverters):
        self.__output = output
        self.__accounts = BananaAccounts()
        self.__currencyConverters = currencyConverters
        precision = float(config['transferPrecision'])
        self.__minPrecision = 1 - precision
        self.__maxPrecision = 1 + precision

    def write(self, transactions):
        outputFilePath = os.path.join(self.__output, BananaAccounting.__fileName)
        bookings = self.__transform(transactions)
        bookings = sorted(bookings, key=lambda b: b[0])
        with open(outputFilePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['Datum', 'Beleg', 'Beschreibung', 'KtSoll', 'KtHaben', 'Betr.Währung', 'Währung', 'Wechselkurs', 'Betrag CHF', 'Anteile', 'KS1', 'Bemerkungen'])
            writer.writerows(booking[1] for booking in bookings)

    def __transform(self, transactions):
        transfers = list()
        self.__transactions = sorted(transactions, key=lambda t: t.dateTime.timestamp())
        for transaction in self.__transactions:
            if issubclass(type(transaction), Trade):
                yield from self.__transformTrade(transaction)
            elif isinstance(transaction, MarginTrade):
                yield from self.__transformMarginTrade(transaction)
            elif issubclass(type(transaction), Transfer):
                transfers.append(transaction)
            elif isinstance(transaction, Reimbursement):
                yield from self.__transformReimbursement(transaction)
            elif isinstance(transaction, Payment):
                yield from self.__transformPayment(transaction)
            elif isinstance(transaction, Covesting):
                yield from self.__transformCovesting(transaction)
            elif isinstance(transaction, EnterLobby):
                yield from self.__transformEnterLobby(transaction)
            elif isinstance(transaction, ExitLobby):
                yield from self.__transformExitLobby(transaction)
            elif isinstance(transaction, StartStake):
                yield from self.__transformStartStake(transaction)
            elif isinstance(transaction, EndStake):
                yield from self.__transformEndStake(transaction)
            else:
                BananaAccounting.__log.error("Unknown transaction; class='%s'", type(transaction).__name__)
                raise ValueError("Unknown transaction; type='{}'".format(type(transaction)))
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

    def __transformMarginTrade(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        account = self.__accounts.get(transaction.unit, transaction.mergentId)
        exchangeRate = self.__currencyConverters.exchangeRate(transaction.unit, transaction.dateTime.date())
        baseCurrencyEntryFee = round(transaction.entryFee * exchangeRate, 2)
        baseCurrencyAmount = round(transaction.amount * exchangeRate, 2)
        baseCurrencyExitFee  = round(transaction.exitFee * exchangeRate, 2)
        costCenter = '{0}{1}'.format(transaction.unit, transaction.mergentId)
        #                    date,    receipt,        description,               deposit,                withdrawal,             amount,                  currency,         exchangeRate, baseCurrencyAmount,   shares, costCenter1
        if transaction.entryFee > 0:
            yield (date[0], [date[1], transaction.id, 'Margin Trade - Einstieg', self.__accounts.fees,   account,                transaction.entryFee,    transaction.unit, exchangeRate, baseCurrencyEntryFee, '',     '-'+costCenter])
        if transaction.amount >= 0:
            BananaAccounting.__log.debug("Margin gain; %s, %s %s", transaction.mergentId, transaction.amount, transaction.unit)
            yield (date[0], [date[1], transaction.id, 'Margin Trade - Gewinn',   account,                self.__accounts.equity, transaction.amount,      transaction.unit, exchangeRate, baseCurrencyAmount,   '',     costCenter])
        else:
            BananaAccounting.__log.debug("Margin loss; %s, %s %s", transaction.mergentId, abs(transaction.amount), transaction.unit)
            yield (date[0], [date[1], transaction.id, 'Margin Trade - Verlust',  self.__accounts.equity, account,                abs(transaction.amount), transaction.unit, exchangeRate, baseCurrencyAmount,   '',     '-'+costCenter])
        yield     (date[0], [date[1], transaction.id, 'Margin Trade - Ausstieg', self.__accounts.fees,   account,                transaction.exitFee,     transaction.unit, exchangeRate, baseCurrencyExitFee,  '',     '-'+costCenter])

    def __transformTransfers(self, transfers):
        sortedByDate = sorted(transfers, key=lambda t:t.dateTime.date())
        groupedByDate = itertools.groupby(sortedByDate, key=lambda t:t.dateTime.date())
        for _, dateGroup in groupedByDate:
            dateGroup = list(dateGroup)
            deposits = [transfer for transfer in dateGroup if isinstance(transfer, DepositTransfer)]
            withdrawals = [transfer for transfer in dateGroup if isinstance(transfer, WithdrawTransfer)]
            for deposit in deposits:
                matches = [w for w in withdrawals if self.__matchingTransfers(w, deposit)]
                if len(matches) == 0:
                    yield from self.__transformSingleTransfer(deposit)
                elif len(matches) == 1:
                    withdrawals.remove(matches[0])
                    yield from self.__transformDoubleTransfers(deposit, matches[0])
                else:
                    BananaAccounting.__log.error("Multiple matching transfers; deposit=%s, matches=[%s]", deposit, ','.join([match.__str__() for match in matches]))
                    yield from self.__transformSingleTransfer(deposit)
            for w in withdrawals:
                yield from self.__transformSingleTransfer(w)

    def __matchingTransfers(self, withdrawal, deposit):
        if withdrawal.mergentId == deposit.mergentId:
            return False
        if withdrawal.dateTime.date() != deposit.dateTime.date():
            return False
        min = deposit.amount * self.__minPrecision
        max = deposit.amount * self.__maxPrecision
        if withdrawal.amount <= min:
            return False
        if max <= withdrawal.amount:
            return False
        return True

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
                description = 'Transfer von UNBEKANNT'
                #                date,    receipt,        description, debit,                credit,  amount,             currency,         exchangeRate, baseCurrencyAmount,    shares, costCenter1
                yield (date[0], [date[1], transaction.id, description, account,              '',      transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount,    '',     costCenter])
        elif isinstance(transaction, WithdrawTransfer):
            if CurrencyConverters.isFiat(transaction.unit):
                BananaAccounting.__log.debug("Withdraw; %s, %s %s", transaction.mergentId, transaction.amount, transaction.unit)
                description = 'Auszahlung'
            else:
                BananaAccounting.__log.warn("Transfer; %s->???, %s %s", transaction.mergentId, transaction.amount, transaction.unit)
                description = 'Transfer nach UNBEKANNT'
            #                    date,    receipt,        description, debit,                  credit,  amount,             currency,         exchangeRate, baseCurrencyAmount,    shares, costCenter1
            yield     (date[0], [date[1], transaction.id, description, self.__accounts.equity, account, transaction.amount, transaction.unit, exchangeRate, baseCurrencyAmount,    '',     '-'+costCenter])
            if transaction.fee > 0:
                baseCurrencyFeeAmount = round(transaction.fee * exchangeRate, 2)
                yield (date[0], [date[1], '',             description, self.__accounts.fees,   account, transaction.fee,    transaction.unit, exchangeRate, baseCurrencyFeeAmount, '',     '-'+costCenter])


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
        baseCurrencyDeposit = round(deposit.amount * exchangeRate, 2)
        baseCurrencyWithdrawal = round(withdrawal.amount * exchangeRate, 2)
        fee = withdrawal.fee if withdrawal.fee > 0 else withdrawal.amount - deposit.amount
        baseCurrencyFee = round(withdrawal.fee * exchangeRate, 2)
        # target                       date,              receipt,       description,           deposit,              withdrawal,        amount,            currency,        exchangeRate, baseCurrencyAmount,     shares, costCenter1
        yield     (depositDate[0],    [depositDate[1],    deposit.id,    depositDescription,    depositAccount,       '',                deposit.amount,    deposit.unit,    exchangeRate, baseCurrencyDeposit,    '',     depositCostCenter])
        # source
        yield     (withdrawalDate[0], [withdrawalDate[1], withdrawal.id, withdrawalDescription, '',                   withdrawalAccount, withdrawal.amount, withdrawal.unit, exchangeRate, baseCurrencyWithdrawal, '',     '-'+withdrawalCostCenter])
        if fee > 0:
            yield (withdrawalDate[0], [withdrawalDate[1], '',            withdrawalDescription, self.__accounts.fees, withdrawalAccount, fee,               withdrawal.unit, exchangeRate, baseCurrencyFee,        '',     '-'+withdrawalCostCenter])

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

    def __transformCovesting(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        account = self.__accounts.get(transaction.unit, transaction.mergentId)
        exchangeRate = self.__currencyConverters.exchangeRate(transaction.unit, transaction.dateTime.date())
        baseCurrencyEntryFee = round(transaction.entryFee * exchangeRate, 2)
        baseCurrencyAmount = round(transaction.amount * exchangeRate, 2)
        baseCurrencyExitFee  = round(transaction.exitFee * exchangeRate, 2)
        costCenter = '{0}{1}'.format(transaction.unit, transaction.mergentId)
        #                    date,    receipt,        description,                                     deposit,                withdrawal,             amount,                  currency,         exchangeRate, baseCurrencyAmount,   shares, costCenter1
        if transaction.entryFee > 0:
            yield (date[0], [date[1], transaction.id, '{} - Startgebühren'.format(transaction.trader), self.__accounts.fees,   account,                transaction.entryFee,    transaction.unit, exchangeRate, baseCurrencyEntryFee, '',     '-'+costCenter])
        if transaction.amount >= 0:
            BananaAccounting.__log.debug("Covesting gain; %s, %s, %s %s, %s", transaction.mergentId, transaction.trader, transaction.amount, transaction.unit, transaction.note)
            yield (date[0], [date[1], transaction.id, '{} - Gewinn'.format(transaction.trader),        account,                self.__accounts.equity, transaction.amount,      transaction.unit, exchangeRate, baseCurrencyAmount,   '',     costCenter])
        else:
            BananaAccounting.__log.debug("Covesting loss; %s, %s, %s %s, %s", transaction.mergentId, transaction.trader, abs(transaction.amount), transaction.unit, transaction.note)
            yield (date[0], [date[1], transaction.id, '{} - Verlust'.format(transaction.trader),       self.__accounts.equity, account,                abs(transaction.amount), transaction.unit, exchangeRate, baseCurrencyAmount,   '',     '-'+costCenter])
        yield     (date[0], [date[1], transaction.id, '{} - Gebühren'.format(transaction.trader),      self.__accounts.fees,   account,                transaction.exitFee,     transaction.unit, exchangeRate, baseCurrencyExitFee,  '',     '-'+costCenter])

    def __transformEnterLobby(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Lobby; Enter'.format(transaction.unit)
        accountWithdrawal = self.__accounts.get(transaction.unit, transaction.mergentId)
        accountLobby = self.__accounts.get(transaction.unit, transaction.lobby)
        exchangeRateAmount = self.__currencyConverters.exchangeRate(transaction.unit, transaction.dateTime.date())
        exchangeRateFee = self.__currencyConverters.exchangeRate(transaction.unit, transaction.dateTime.date())
        baseCurrencyAmount = round(transaction.amount * exchangeRateAmount, 2)
        baseCurrencyFee  = round(transaction.fee * exchangeRateFee, 2)
        costCenterWithdrawal = '{0}{1}'.format(transaction.unit, transaction.mergentId)
        costCenterLobby = '{0}{1}'.format(transaction.unit, transaction.lobby)
        BananaAccounting.__log.debug("Lobby enter; %s, %s %s", transaction.lobby, transaction.amount, transaction.unit)
        # withdrawal     date,    receipt,        description, deposit,              withdrawal,        amount,             currency,         exchangeRate,       baseCurrencyAmount, shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, '',                   accountWithdrawal, transaction.amount, transaction.unit, exchangeRateAmount, baseCurrencyAmount, '',     '-'+costCenterWithdrawal])
        # deposit
        yield (date[0], [date[1], transaction.id, description, accountLobby,         '',                transaction.amount, transaction.unit, exchangeRateAmount, baseCurrencyAmount, '',     costCenterLobby])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, accountWithdrawal, transaction.fee,    transaction.unit, exchangeRateFee,    baseCurrencyFee,    '',     '-'+costCenterWithdrawal])

    def __transformExitLobby(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Lobby; Exit'.format(transaction.unitLobby)
        amountWithdrawal = self.__accounts.get(transaction.unit, transaction.unitLobby)
        accountDeposit = self.__accounts.get(transaction.unitLobby, transaction.mergentId)
        accountFee = self.__accounts.get(transaction.unit, transaction.mergentId)
        exchangeRateLobby = self.__currencyConverters.exchangeRate(transaction.unitLobby, transaction.dateTime.date())
        exchangeRateUnit = self.__currencyConverters.exchangeRate(transaction.unit, transaction.dateTime.date())
        baseCurrencyWithdrawal  = round(transaction.amount * exchangeRateUnit, 2)
        baseCurrencyDeposit  = round(transaction.amountLobby * exchangeRateLobby, 2)
        baseCurrencyFee  = round(transaction.fee * exchangeRateUnit, 2)
        costCenterWithdrawal = '{0}{1}'.format(transaction.unit, transaction.unitLobby)
        costCenterDeposit = '{0}{1}'.format(transaction.unitLobby, transaction.mergentId)
        costCenterFee = '{0}{1}'.format(transaction.unit, transaction.mergentId)
        BananaAccounting.__log.debug("Lobby exit; %s %s", transaction.amountLobby, transaction.unitLobby)
        # withdrawal     date,    receipt,        description, deposit,              withdrawal,       amount,                  currency,              exchangeRate,      baseCurrencyAmount,     shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, '',                   amountWithdrawal, transaction.amount,      transaction.unit,      exchangeRateUnit,  baseCurrencyWithdrawal, '',     '-'+costCenterWithdrawal])
        # deposit
        yield (date[0], [date[1], transaction.id, description, accountDeposit,       '',               transaction.amountLobby, transaction.unitLobby, exchangeRateLobby, baseCurrencyDeposit,    '',     costCenterDeposit])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, accountFee,       transaction.fee,         transaction.unit,      exchangeRateUnit,  baseCurrencyFee,        '',     '-'+costCenterFee])

    def __transformStartStake(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Stake; Start'.format(transaction.unitAmount)
        accountWithdrawal = self.__accounts.get(transaction.unitAmount, transaction.mergentId)
        accountDeposit = self.__accounts.get(transaction.unitAmount, self.__accounts.staked)
        accountFee = self.__accounts.get(transaction.unitFee, transaction.mergentId)
        exchangeRateAmount = self.__currencyConverters.exchangeRate(transaction.unitAmount, transaction.dateTime.date())
        exchangeRateFee = self.__currencyConverters.exchangeRate(transaction.unitFee, transaction.dateTime.date())
        baseCurrencyAmount = round(transaction.amount * exchangeRateAmount, 2)
        baseCurrencyFee  = round(transaction.fee * exchangeRateFee, 2)
        costCenterWithdrawal = '-{0}{1}'.format(transaction.unitAmount, transaction.mergentId)
        costCenterDeposit = '{0}{1}'.format(transaction.unitAmount, self.__accounts.staked)
        costCenterFee = '-{0}{1}'.format(transaction.unitFee, transaction.mergentId)
        BananaAccounting.__log.debug("Stake start; %s, %s %s", transaction.mergentId, transaction.amount, transaction.unitAmount)
        # withdrawal     date,    receipt,        description, deposit,              withdrawal,        amount,             currency,               exchangeRate,      baseCurrencyAmount,   shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, '',                   accountWithdrawal, transaction.amount, transaction.unitAmount, exchangeRateAmount, baseCurrencyAmount,  '',     costCenterWithdrawal])
        # deposit
        yield (date[0], [date[1], transaction.id, description, accountDeposit,       '',                transaction.amount, transaction.unitAmount, exchangeRateAmount, baseCurrencyAmount,  '',     costCenterDeposit])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, accountFee,        transaction.fee,    transaction.unitFee,    exchangeRateFee,    baseCurrencyFee,     '',     costCenterFee])

    def __transformEndStake(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Stake; End'.format(transaction.unitAmount)
        accountDeposit = self.__accounts.get(transaction.unitAmount, transaction.mergentId)
        accountWithdrawal = self.__accounts.get(transaction.unitAmount, self.__accounts.staked)
        accountFee = self.__accounts.get(transaction.unitFee, transaction.mergentId)
        exchangeRateAmount = self.__currencyConverters.exchangeRate(transaction.unitAmount, transaction.dateTime.date())
        exchangeRateFee = self.__currencyConverters.exchangeRate(transaction.unitFee, transaction.dateTime.date())
        baseCurrencyAmount = round(transaction.amount * exchangeRateAmount, 2)
        baseCurrencyFee  = round(transaction.fee * exchangeRateFee, 2)
        costCenterDeposit = '{0}{1}'.format(transaction.unitAmount, transaction.mergentId)
        costCenterWithdrawal = '-{0}{1}'.format(transaction.unitAmount, self.__accounts.staked)
        costCenterFee = '-{0}{1}'.format(transaction.unitFee, transaction.mergentId)
        BananaAccounting.__log.debug("Stake end; %s, %s %s", transaction.mergentId, transaction.amount, transaction.unitAmount)
        # deposit        date,    receipt,        description, deposit,              withdrawal,        amount,             currency,               exchangeRate,      baseCurrencyAmount,   shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, accountDeposit,       '',                transaction.amount, transaction.unitAmount, exchangeRateAmount, baseCurrencyAmount,  '',     costCenterDeposit])
        # withdrawal
        yield (date[0], [date[1], transaction.id, description, '',                   accountWithdrawal, transaction.amount, transaction.unitAmount, exchangeRateAmount, baseCurrencyAmount,  '',     costCenterWithdrawal])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, accountFee,        transaction.fee,    transaction.unitFee,    exchangeRateFee,    baseCurrencyFee,     '',     costCenterFee])

    @staticmethod
    def __getDate(transaction):
        return [transaction.dateTime.date(), transaction.dateTime.date().strftime('%d.%m.%Y')]
