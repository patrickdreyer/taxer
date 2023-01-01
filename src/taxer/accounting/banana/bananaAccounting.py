import csv
from datetime import timedelta
from decimal import Decimal
import logging
import os

from ...transactions.buyTrade import BuyTrade
from ...transactions.cancelFee import CancelFee
from ...transactions.covesting import Covesting
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.endStake import EndStake
from ...transactions.enterLobby import EnterLobby
from ...transactions.exitLobby import ExitLobby
from ...transactions.marginTrade import MarginTrade
from ...transactions.mint import Mint
from ...transactions.payment import Payment
from ...transactions.reimbursement import Reimbursement
from ...transactions.sellTrade import SellTrade
from ...transactions.startStake import StartStake
from ...transactions.trade import Trade
from ...transactions.transfer import Transfer
from ...transactions.withdrawTransfer import WithdrawTransfer
from ..accounting import Accounting
from ..costCenter import CostCenter
from .bananaAccounts import BananaAccounts
from .bananaCurrency import BananaCurrency


class BananaAccounting(Accounting):
    __fileName = 'banana.csv'

    __log = logging.getLogger(__name__)

    def __init__(self, output, config, currencyConverters):
        self.__output = output
        self.__accounts = BananaAccounts(config['accounts'])
        self.__currencyConverters = currencyConverters
        precision = Decimal(config['transferPrecision'])
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
        self.__accountedTransferIds = set()
        transfers = list()
        for transaction in transactions:
            if issubclass(type(transaction), Trade):
                yield from self.__transformTrade(transaction)
            elif isinstance(transaction, MarginTrade):
                yield from self.__transformMarginTrade(transaction)
            elif isinstance(transaction, CancelFee):
                yield from self.__transformCancelFee(transaction)
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
            elif issubclass(type(transaction), Transfer):
                transfers.append(transaction)
            elif isinstance(transaction, Mint):
                yield from self.__transformMint(transaction)
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
                BananaAccounting.__log.debug("%s - Buy; %s, %s", transaction.dateTime, transaction.mergentId, b)
                description = 'Kauf; {0}'.format(transaction.buy.unit)
                # fiat           date,    receipt,        description, debit,                    credit,                   amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
                yield (date[0], [date[1], transaction.id, description, self.__accounts.transfer, s.account,                s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount, '',     s.costCenter.minus()])
                # crypto
                yield (date[0], [date[1], transaction.id, description, b.account,                self.__accounts.transfer, b.amount, b.unit,   b.baseCurrency.exchangeRate, b.baseCurrency.amount, '',     b.costCenter])
                # fee
                yield (date[0], [date[1], transaction.id, description, self.__accounts.fees,     s.account,                f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])
            elif isinstance(transaction, SellTrade):
                BananaAccounting.__log.debug("%s - Sell; %s, %s", transaction.dateTime,transaction.mergentId, s)
                description = 'Verkauf; {0}'.format(transaction.sell.unit)
                # crypto         date,    receipt,        description, debit,                    credit,                   amount,   currency, exchangeRate,                baseCurrencyAmount,     shares, costCenter1
                yield (date[0], [date[1], transaction.id, description, self.__accounts.transfer, s.account,                s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount,  '',     s.costCenter.minus()])
                # fiat
                yield (date[0], [date[1], transaction.id, description, b.account,                self.__accounts.transfer, b.amount, b.unit,   b.baseCurrency.exchangeRate, b.baseCurrency.amount,  '',     b.costCenter])
                # fee
                yield (date[0], [date[1], transaction.id, description, self.__accounts.fees,     self.__accounts.transfer, f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount , '',     ''])

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
            BananaAccounting.__log.debug("%s - Margin gain; %s, %s", transaction.dateTime, transaction.mergentId, a)
            yield (date[0], [date[1], transaction.id, 'Margin Trade - Gewinn',   a.account,              self.__accounts.equity, a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, '',    a.costCenter])
        else:
            BananaAccounting.__log.debug("%s - Margin loss; %s, %s", transaction.dateTime, transaction.mergentId, a)
            yield (date[0], [date[1], transaction.id, 'Margin Trade - Verlust',  self.__accounts.equity, a.account,              a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, '',    a.costCenter.minus()])
        yield     (date[0], [date[1], transaction.id, 'Margin Trade - Ausstieg', self.__accounts.fees,   a.account,              x.amount, a.unit,   x.baseCurrency.exchangeRate, x.baseCurrency.amount, '',    x.costCenter.minus()])

    def __transformTransfers(self, transfers):
        transfers.sort(key=lambda t: t.dateTime)

        # repeat as long as at least one match was found
        atLeastOnce = True
        while atLeastOnce:
            atLeastOnce = False
            for transfer in transfers:
                if transfer.id in self.__accountedTransferIds:
                    continue
                atLeastOnce = True

                if isinstance(transfer, DepositTransfer):
                    nonAccountedPastWithdraws = [t for t in transfers if self.__nonAccounted(WithdrawTransfer, transfer.dateTime - timedelta(days=1), transfer.dateTime + timedelta(hours=1), t)]
                    matches = [withdrawal for withdrawal in nonAccountedPastWithdraws if self.__matchingTransfers(withdrawal, transfer)]
                    if len(matches) == 0:
                        yield from self.__transformSingleTransfer(transfer)
                    else:
                        yield from self.__transformDoubleTransfers(transfer, matches[0])
                elif isinstance(transfer, WithdrawTransfer):
                    nonAccountedFutureDeposits = [t for t in transfers if self.__nonAccounted(DepositTransfer, transfer.dateTime - timedelta(hours=1), transfer.dateTime + timedelta(days=1), t)]
                    matches = [deposit for deposit in nonAccountedFutureDeposits if self.__matchingTransfers(deposit, transfer)]
                    if len(matches) == 0:
                        yield from self.__transformSingleTransfer(transfer)
                    else:
                        yield from self.__transformDoubleTransfers(matches[0], transfer)
        nonAccounted = [t for t in transfers if not transfer.id in self.__accountedTransferIds]
        for t in nonAccounted:
            BananaAccounting.__log.debug("Non accounted transfer; %s, %s, %s", transfer.dateTime, transfer.mergentId, transfer.amount)


    def __nonAccounted(self, type, earlierstDateTime, latestDateTime, transfer):
        return isinstance(transfer, type) \
            and not transfer.id in self.__accountedTransferIds \
                and earlierstDateTime <= transfer.dateTime and transfer.dateTime <= latestDateTime

    def __matchingTransfers(self, withdrawal, deposit):
        if withdrawal.mergentId == deposit.mergentId:
            return False
        depositTotal = deposit.amount + deposit.fee
        min = depositTotal.amount * self.__minPrecision
        max = depositTotal.amount * self.__maxPrecision
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
                BananaAccounting.__log.debug("%s - Deposit; %s, %s", transaction.dateTime, transaction.mergentId, c)
                #                date,    receipt,        description,  debit,     credit,                 amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
                yield (date[0], [date[1], transaction.id, 'Einzahlung', c.account, self.__accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])
            else:
                BananaAccounting.__log.warn("%s - Transfer; ???->%s, %s, id=%s, address=%s", transaction.dateTime, transaction.mergentId, transaction.amount, transaction.id, transaction.address)
                description = 'Transfer ? -> {}'.format(transaction.mergentId)
                #                date,    receipt,        description, debit,     credit, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
                yield (date[0], [date[1], transaction.id, description, c.account, '',     c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])
        elif isinstance(transaction, WithdrawTransfer):
            if c.isFiat:
                BananaAccounting.__log.debug("%s - Withdraw; %s, %s", transaction.dateTime, transaction.mergentId, c)
                description = 'Auszahlung'
            else:
                BananaAccounting.__log.warn("%s - Transfer; %s->???, %s, id=%s, address=%s", transaction.dateTime, transaction.mergentId, c, transaction.id, transaction.address)
                description = 'Transfer {} -> ?'.format(transaction.mergentId)
            #                    date,    receipt,        description, debit,                  credit,    amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
            yield     (date[0], [date[1], transaction.id, description, self.__accounts.equity, c.account, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter.minus()])
            if transaction.fee.amount > 0:
                f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
                yield (date[0], [date[1], '',             description, self.__accounts.fees,   c.account, f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     c.costCenter.minus()])
        self.__accountedTransferIds.add(transaction.id)

    def __transformDoubleTransfers(self, deposit, withdrawal):
        BananaAccounting.__log.debug("%s - Transfer; %s->%s, %s", withdrawal.dateTime, withdrawal.mergentId, deposit.mergentId, deposit.amount)
        dDate = BananaAccounting.__getDate(deposit)
        description = 'Transfer {} -> {}'.format(withdrawal.mergentId, deposit.mergentId)
        d = BananaCurrency(self.__accounts, self.__currencyConverters, deposit.amount, deposit)
        wDate = BananaAccounting.__getDate(withdrawal)
        w = BananaCurrency(self.__accounts, self.__currencyConverters, withdrawal.amount, withdrawal)
        if withdrawal.fee.amount > 0 and deposit.fee.amount > 0:
            BananaAccounting.__log.warn("Double transfer fees; %s, %s - %s. %s", withdrawal.mergentId, withdrawal.fee, deposit.mergentId, deposit.fee)
        # target                  date,     receipt,       description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield         (dDate[0], [dDate[1], deposit.id,    description, d.account,            '',         d.amount, d.unit,   d.baseCurrency.exchangeRate, d.baseCurrency.amount, '',     d.costCenter])
        if deposit.fee.amount > 0:
            f = BananaCurrency(self.__accounts, self.__currencyConverters, deposit.fee, deposit)
            yield     (wDate[0], [wDate[1], '',            description, self.__accounts.fees, '',         f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])
        # source
        yield         (wDate[0], [wDate[1], withdrawal.id, description, '',                   w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     w.costCenter.minus()])
        if withdrawal.fee.amount > 0:
            f = BananaCurrency(self.__accounts, self.__currencyConverters, withdrawal.fee, withdrawal)
            yield     (wDate[0], [wDate[1], '',            description, self.__accounts.fees, f.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])
        self.__accountedTransferIds.add(deposit.id)
        self.__accountedTransferIds.add(withdrawal.id)

    def __transformCancelFee(self, transaction):
        BananaAccounting.__log.debug("%s - Cancel fee; %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount)
        date = BananaAccounting.__getDate(transaction)
        c = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        #                date,    receipt,        description,     deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, 'Abbruchgebühr', self.__accounts.fees, c.account,  c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter.minus()])

    def __transformReimbursement(self, transaction):
        BananaAccounting.__log.debug("%s - Reimbursement; %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount)
        date = BananaAccounting.__getDate(transaction)
        c = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        #                date,    receipt,        description,      deposit,   withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, 'Rückerstattung', c.account, self.__accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])

    def __transformPayment(self, transaction):
        BananaAccounting.__log.debug("%s - Payment; %s, %s, %s", transaction.dateTime, transaction.mergentId, transaction.amount, transaction.note)
        date = BananaAccounting.__getDate(transaction)
        description = f'Bezahlung; {transaction.note}'
        w = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        #                    date,    receipt,        description, deposit,                withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield     (date[0], [date[1], transaction.id, description, self.__accounts.equity, w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     w.costCenter.minus(), transaction.note])
        if transaction.fee.amount > 0:
            f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
            yield (date[0], [date[1], '',             description, self.__accounts.fees,   w.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])

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
            BananaAccounting.__log.debug("%s - Covesting gain; %s, %s, %s, %s", transaction.dateTime, transaction.mergentId, transaction.trader, a, transaction.note)
            yield (date[0], [date[1], transaction.id, '{} - Gewinn'.format(transaction.trader),        a.account,              self.__accounts.equity, a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, '',    a.costCenter])
        else:
            BananaAccounting.__log.debug("%s - Covesting loss; %s, %s, %s, %s", transaction.dateTime, transaction.mergentId, transaction.trader, a, transaction.note)
            yield (date[0], [date[1], transaction.id, '{} - Verlust'.format(transaction.trader),       self.__accounts.equity, a.account,              a.amount, a.unit,   a.baseCurrency.exchangeRate, a.baseCurrency.amount, '',    a.costCenter.minus()])
        if x.amount > 0:
            yield (date[0], [date[1], transaction.id, '{} - Gebühren'.format(transaction.trader),      self.__accounts.fees,   x.account,              x.amount, x.unit,   x.baseCurrency.exchangeRate, x.baseCurrency.amount, '',    x.costCenter.minus()])

    def __transformEnterLobby(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Lobby; Enter'.format(transaction.lobby)
        w = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        lAccount = self.__accounts.get(transaction.amount.unit, transaction.lobby)
        lCostCenter = CostCenter(transaction.lobby, transaction.amount)
        BananaAccounting.__log.debug("%s - Lobby enter; %s, %s", transaction.dateTime, transaction.lobby, transaction.amount)
        # withdrawal     date,    receipt,        description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, '',                   w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     w.costCenter.minus()])
        # lobby
        yield (date[0], [date[1], transaction.id, description, lAccount,             '',         w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     lCostCenter])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, w.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     w.costCenter.minus()])

    def __transformExitLobby(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Lobby; Exit'.format(transaction.lobby.unit)
        l = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.lobby, transaction.amount.unit, transaction.dateTime)
        d = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        BananaAccounting.__log.debug("%s - Lobby exit; %s -> %s", transaction.dateTime, transaction.lobby, transaction.amount)
        # lobby          date,    receipt,        description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, '',                   l.account,  l.amount, l.unit,   l.baseCurrency.exchangeRate, l.baseCurrency.amount, '',     l.costCenter.minus()])
        # deposit
        yield (date[0], [date[1], transaction.id, description, d.account,            '',         d.amount, d.unit,   d.baseCurrency.exchangeRate, d.baseCurrency.amount, '',     d.costCenter])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, f.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])

    def __transformStartStake(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Stake; Start'.format(transaction.amount.unit)
        w = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        s = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, self.__accounts.staked, transaction.dateTime)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        BananaAccounting.__log.debug("%s - Stake start; %s", transaction.dateTime, transaction.amount)
        # withdrawal     date,    receipt,        description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, '',                   w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     w.costCenter.minus()])
        # stake
        yield (date[0], [date[1], transaction.id, description, s.account,            '',         s.amount, s.unit,   s.baseCurrency.exchangeRate, s.baseCurrency.amount, '',     s.costCenter])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, f.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])

    def __transformEndStake(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Stake; End'.format(transaction.amount.unit)
        u = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, self.__accounts.staked, transaction.dateTime)
        d = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.total, transaction)
        i = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.interest, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        BananaAccounting.__log.debug("%s - Stake end; %s", transaction.dateTime, transaction.amount)
        # deposit        date,    receipt,        description, deposit,              withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, d.account,            '',                     d.amount, d.unit,   d.baseCurrency.exchangeRate, d.baseCurrency.amount, '',     d.costCenter])
        # unstake
        yield (date[0], [date[1], transaction.id, description, '',                   u.account,              u.amount, u.unit,   u.baseCurrency.exchangeRate, u.baseCurrency.amount, '',     u.costCenter.minus()])
        # interest
        yield (date[0], [date[1], transaction.id, description, '',                   self.__accounts.equity, i.amount, i.unit,   i.baseCurrency.exchangeRate, i.baseCurrency.amount, '',     ''])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, f.account,              f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])

    def __transformMint(self, transaction):
        date = BananaAccounting.__getDate(transaction)
        description = '{} Mint'.format(transaction.amount.unit)
        c = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        BananaAccounting.__log.debug("%s - Mint; %s", transaction.dateTime, transaction.amount)
        # deposit        date,    receipt,        description, deposit,              withdrawal,             amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield (date[0], [date[1], transaction.id, description, c.account,            '',                     c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])
        # claim
        yield (date[0], [date[1], transaction.id, description, '',                   self.__accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     ''])
        # fee
        yield (date[0], [date[1], transaction.id, description, self.__accounts.fees, f.account,              f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])

    @staticmethod
    def __getDate(transaction):
        return [transaction.dateTime.date(), transaction.dateTime.date().strftime('%d.%m.%Y')]
