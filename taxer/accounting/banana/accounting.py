from abc import abstractmethod
import logging
import itertools
import csv
import os
from taxer.accounting import baseCurrency, costCenter

from .accounts import BananaAccounts
from .bananaCurrency import BananaCurrency
from ..accounting import Accounting
from ...currencyConverters.currencyConverters import CurrencyConverters
from ...transactions.currency import Currency
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
            s = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.sell, transaction)
            b = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.buy, transaction)
            f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
            if isinstance(transaction, BuyTrade):
                BananaAccounting.__log.debug("Buy; %s, %s", transaction.mergentId, b)
                description = 'Kauf; {0}'.format(transaction.buy.unit)
                # fiat           date,    receipt,        description, debit,                    credit,                   amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
                yield (date[0], [date[1], transaction.id, description, self.__accounts.transfer, s.account,                s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount, '',     s.costCenter.minus()])
                # crypto
                yield (date[0], [date[1], transaction.id, description, b.account,                self.__accounts.transfer, b.amount, b.unit,   b.baseCurrency.exchangeRate, b.baseCurrency.amount, '',     b.costCenter])
                # fee
                yield (date[0], [date[1], transaction.id, description, self.__accounts.fees,     s.account,                f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])
            elif isinstance(transaction, SellTrade):
                BananaAccounting.__log.debug("Sell; %s, %s", transaction.mergentId, s)
                description = 'Verkauf; {0}'.format(transaction.sell.unit)
                # crypto         date,    receipt,        description, debit,                    credit,                   amount,   currency, exchangeRate,                baseCurrencyAmount,     shares, costCenter1
                yield (date[0], [date[1], transaction.id, description, self.__accounts.transfer, s.account,                s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount,  '',     s.costCenter.minus()])
                # fiat
                yield (date[0], [date[1], transaction.id, description, b.account,                self.__accounts.transfer, b.amount, b.unit,   b.baseCurrency.exchangeRate, b.baseCurrency.amount,  '',     b.costCenter])
                # fee
                yield (date[0], [date[1], transaction.id, description, self.__accounts.fees,     s.account,                f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount , '',     f.costCenter.minus()])

    def __transformMarginTrade(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        # gain/loss
        a = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        # entry fee
        e = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.entryFee, transaction)
        # exit fee
        x = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.exitFee, transaction)
        #                    date,    receipt,        description,               deposit,                withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,   shares, costCenter1
        if e.amount > 0:
            yield (date[0], [date[1], transaction.id, 'Margin Trade - Einstieg', self.__accounts.fees,   e.account,              e.amount, e.unit,   e.baseCurrency.exchangeRate, e.baseCurrency.amount, '',    e.costCenter.minus()])
        if a.amountRaw >= 0:
            BananaAccounting.__log.debug("Margin gain; %s, %s", transaction.mergentId, a)
            yield (date[0], [date[1], transaction.id, 'Margin Trade - Gewinn',   a.account,              self.__accounts.equity, a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, '',    a.costCenter])
        else:
            BananaAccounting.__log.debug("Margin loss; %s, %s", transaction.mergentId, a)
            yield (date[0], [date[1], transaction.id, 'Margin Trade - Verlust',  self.__accounts.equity, a.account,              a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, '',    a.costCenter.minus()])
        yield     (date[0], [date[1], transaction.id, 'Margin Trade - Ausstieg', self.__accounts.fees,   a.account,              x.amount, a.unit,   x.baseCurrency.exchangeRate, x.baseCurrency.amount, '',    x.costCenter.minus()])

    def __transformTransfers(self, transfers):
        sortedByDate = sorted(transfers, key=lambda t:t.dateTime.date())
        groupedByDate = itertools.groupby(sortedByDate, key=lambda t:t.dateTime.date())
        for _, dateGroup in groupedByDate:
            dateGroup = list(dateGroup)
            deposits = [transfer for transfer in dateGroup if isinstance(transfer, DepositTransfer)]
            withdrawals = [transfer for transfer in dateGroup if isinstance(transfer, WithdrawTransfer)]
            for deposit in deposits:
                matches = [withdrawal for withdrawal in withdrawals if self.__matchingTransfers(withdrawal, deposit)]
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
        min = deposit.amount.amount * self.__minPrecision
        max = deposit.amount.amount * self.__maxPrecision
        if withdrawal.amount.amount <= min:
            return False
        if max <= withdrawal.amount.amount:
            return False
        return True

    def __transformSingleTransfer(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        c = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        if isinstance(transaction, DepositTransfer):
            if c.isFiat:
                BananaAccounting.__log.debug("Deposit; %s, %s", transaction.mergentId, c)
                #                date,    receipt,        description,  debit,     credit,                 amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
                yield (date[0], [date[1], transaction.id, 'Einzahlung', c.account, self.__accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])
            else:
                BananaAccounting.__log.warn("Transfer; ???->%s, %s", transaction.mergentId, transaction.amount)
                description = 'Transfer von UNBEKANNT'
                #                date,    receipt,        description, debit,     credit, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
                yield (date[0], [date[1], transaction.id, description, c.account, '',     c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])
        elif isinstance(transaction, WithdrawTransfer):
            if c.isFiat:
                BananaAccounting.__log.debug("Withdraw; %s, %s", transaction.mergentId, c)
                description = 'Auszahlung'
            else:
                BananaAccounting.__log.warn("Transfer; %s->???, %s", transaction.mergentId, c)
                description = 'Transfer nach UNBEKANNT'
            #                    date,    receipt,        description, debit,                  credit,    amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
            yield     (date[0], [date[1], transaction.id, description, self.__accounts.equity, c.account, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter.minus()])
            if transaction.fee.amount > 0:
                f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
                yield (date[0], [date[1], '',             description, self.__accounts.fees,   c.account, f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     c.costCenter.minus()])

    def __transformDoubleTransfers(self, deposit, withdrawal):
        BananaAccounting.__log.debug("Transfer; %s->%s, %s", withdrawal.mergentId, deposit.mergentId, deposit)
        dDate = BananaAccounting.__getDate(deposit)
        dDescription = 'Transfer von {0}'.format(withdrawal.mergentId)
        d = BananaCurrency(self.__accounts, self.__currencyConverters, deposit.amount, deposit)
        wDate = BananaAccounting.__getDate(withdrawal)
        wDescription = 'Transfer nach {0}'.format(deposit.mergentId)
        w = BananaCurrency(self.__accounts, self.__currencyConverters, withdrawal.amount, withdrawal)
        fee = withdrawal.fee.amount if withdrawal.fee.amount > 0 else w.amount - d.amount
        baseCurrencyFee = round(fee * w.baseCurrency.exchangeRate, 2)
        # target              date,     receipt,       description,  deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield     (dDate[0], [dDate[1], deposit.id,    dDescription, d.account,            '',         d.amount, d.unit,   d.baseCurrency.exchangeRate, d.baseCurrency.amount, '',     d.costCenter])
        # source
        yield     (wDate[0], [wDate[1], withdrawal.id, wDescription, '',                   w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     w.costCenter.minus()])
        if fee > 0:
            yield (wDate[0], [wDate[1], '',            wDescription, self.__accounts.fees, w.account,  fee,      w.unit,   w.baseCurrency.exchangeRate, baseCurrencyFee,       '',     w.costCenter.minus()])

    def __transformReimbursement(self, transaction):
        BananaAccounting.__log.debug("Reimbursement; %s, %s", transaction.mergentId, transaction.amount)
        date = BananaAccounting.__getDate(transaction)
        c = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        #                date,    receipt,        description,      deposit,   withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, 'Rückerstattung', c.account, self.__accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])

    def __transformPayment(self, transaction):
        BananaAccounting.__log.debug("Payment; %s, %s, %s", transaction.mergentId, transaction.amount, transaction.note)
        date = BananaAccounting.__getDate(transaction)
        c = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        #                date,    receipt,        description, deposit,   withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, 'Bezahlung', c.account, self.__accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter, transaction.note])

    def __transformCovesting(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        # loss/gain
        a = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        # entry fee
        e = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.entryFee, transaction)
        # exit fee
        x = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.exitFee, transaction)
        #                    date,    receipt,        description,                                     deposit,                withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,   shares, costCenter1
        if e.amount > 0:
            yield (date[0], [date[1], transaction.id, '{} - Startgebühren'.format(transaction.trader), self.__accounts.fees,   e.account,              e.amount, e.unit,   e.baseCurrency.exchangeRate, e.baseCurrency.amount, '',    e.costCenter.minus()])
        if a.amountRaw >= 0:
            BananaAccounting.__log.debug("Covesting gain; %s, %s, %s, %s", transaction.mergentId, transaction.trader, a, transaction.note)
            yield (date[0], [date[1], transaction.id, '{} - Gewinn'.format(transaction.trader),        a.account,              self.__accounts.equity, a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, '',    a.costCenter])
        else:
            BananaAccounting.__log.debug("Covesting loss; %s, %s, %s, %s", transaction.mergentId, transaction.trader, a, transaction.note)
            yield (date[0], [date[1], transaction.id, '{} - Verlust'.format(transaction.trader),       self.__accounts.equity, a.account,              a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, '',    a.costCenter.minus()])
        if x.amount > 0:
            yield (date[0], [date[1], transaction.id, '{} - Gebühren'.format(transaction.trader),      self.__accounts.fees,   x.account,              x.amount, x.unit,   x.baseCurrency.exchangeRate, x.baseCurrency.amount, '',    x.costCenter.minus()])

    def __transformEnterLobby(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Lobby; Enter'.format(transaction.lobby)
        w = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        l = BananaCurrency(self.__accounts, self.__currencyConverters, Currency(transaction.lobby, 0), transaction)
        BananaAccounting.__log.debug("Lobby enter; %s, %s", transaction.lobby, transaction.amount)
        # withdrawal     date,    receipt,        description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, '',                   w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     w.costCenter.minus()])
        # lobby
        yield (date[0], [date[1], transaction.id, description, l.account,            '',         w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     l.costCenter])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, w.account,  f.amount, w.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     w.costCenter.minus()])

    def __transformExitLobby(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Lobby; Exit'.format(transaction.lobby.unit)
        l = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.lobby, transaction)
        w = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        BananaAccounting.__log.debug("Lobby exit; %s", transaction.lobby)
        # lobby          date,    receipt,        description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, '',                   w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     w.costCenter.minus()])
        # deposit
        yield (date[0], [date[1], transaction.id, description, l.account,            '',         l.amount, l.unit,   l.baseCurrency.exchangeRate, l.baseCurrency.amount, '',     l.costCenter])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, f.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])

    def __transformStartStake(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Stake; Start'.format(transaction.amount.unit)
        w = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        s = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, self.__accounts.staked, transaction.dateTime)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        BananaAccounting.__log.debug("Stake start; %s", transaction.amount)
        # withdrawal     date,    receipt,        description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, '',                   w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     w.costCenter.minus()])
        # stake
        yield (date[0], [date[1], transaction.id, description, s.account,            '',         s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount, '',     s.costCenter])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, f.account,  f.amount, s.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])

    def __transformEndStake(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Stake; End'.format(transaction.amount.unit)
        u = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, self.__accounts.staked, transaction.dateTime)
        d = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        BananaAccounting.__log.debug("Stake end; %s", transaction.amount)
        # deposit        date,    receipt,        description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, d.account,            '',         d.amount, d.unit,   d.baseCurrency.exchangeRate, d.baseCurrency.amount, '',     d.costCenter])
        # unstake
        yield (date[0], [date[1], transaction.id, description, '',                   u.account,  u.amount, u.unit,   u.baseCurrency.exchangeRate, u.baseCurrency.amount, '',     u.costCenter.minus()])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, f.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])

    @staticmethod
    def __getDate(transaction):
        return [transaction.dateTime.date(), transaction.dateTime.date().strftime('%d.%m.%Y')]
