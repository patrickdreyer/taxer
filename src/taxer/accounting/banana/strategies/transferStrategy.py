from datetime import timedelta
from decimal import Decimal
import logging

from ....transactions.depositTransfer import DepositTransfer
from ....transactions.payment import Payment
from ....transactions.transfer import Transfer
from ....transactions.withdrawTransfer import WithdrawTransfer
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class TransferStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters
        precision = Decimal(config['transferPrecision'])
        self.__minPrecision = 1 - precision
        self.__maxPrecision = 1 + precision

    def initialize(self):
        self.__transfers = []
        self.__accountedTransferIds = set()

    def finalize(self):
        self.__transfers.sort(key=lambda t: t.dateTime)

        # repeat as long as at least one match was found
        atLeastOnce = True
        while atLeastOnce:
            atLeastOnce = False
            for transfer in self.__transfers:
                if transfer.id in self.__accountedTransferIds:
                    continue
                atLeastOnce = True

                if isinstance(transfer, DepositTransfer):
                    nonAccountedPastWithdraws = [t for t in self.__transfers if self.__nonAccounted(WithdrawTransfer, transfer.dateTime - timedelta(days=1), transfer.dateTime + timedelta(hours=1), t)]
                    matches = [w for w in nonAccountedPastWithdraws if self.__matchingTransfers(w, transfer)]
                    if len(matches) == 0:
                        yield from self.__transformSingleTransfer(transfer)
                    else:
                        yield from self.__transformDoubleTransfers(transfer, matches[0])
                elif isinstance(transfer, WithdrawTransfer):
                    nonAccountedFutureDeposits = [t for t in self.__transfers if self.__nonAccounted(DepositTransfer, transfer.dateTime - timedelta(hours=1), transfer.dateTime + timedelta(days=1), t)]
                    matches = [deposit for deposit in nonAccountedFutureDeposits if self.__matchingTransfers(deposit, transfer)]
                    if len(matches) == 0:
                        yield from self.__transformSingleTransfer(transfer)
                    else:
                        yield from self.__transformDoubleTransfers(matches[0], transfer)
        nonAccounted = [t for t in self.__transfers if not transfer.id in self.__accountedTransferIds]
        for t in nonAccounted:
            TransferStrategy.__log.debug("Non accounted transfer; %s, %s, %s", t.dateTime, t.mergentId, t.amount)

    def doesTransform(self, transaction):
        return issubclass(type(transaction), Transfer) and not isinstance(transaction, Payment)

    def transform(self, transaction):
        self.__transfers.append(transaction)
        yield from []

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
        c = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount, transaction)
        if isinstance(transaction, DepositTransfer):
            if c.isFiat:
                TransferStrategy.__log.debug("%s - Deposit; %s, %s", transaction.dateTime, transaction.mergentId, c)
                #                                    date,                          receipt,        description,  debit,     credit,                 amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
                yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, 'Einzahlung', c.account, self.__accounts.equity, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])
            else:
                TransferStrategy.__log.warn("%s - Transfer; ???->%s, %s, id=%s, address=%s", transaction.dateTime, transaction.mergentId, transaction.amount, transaction.id, transaction.address)
                description = 'Transfer ? -> {}'.format(transaction.mergentId)
                #                                    date,                          receipt,        description, debit,     credit, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
                yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, c.account, '',     c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter])
        elif isinstance(transaction, WithdrawTransfer):
            if c.isFiat:
                TransferStrategy.__log.debug("%s - Withdraw; %s, %s", transaction.dateTime, transaction.mergentId, c)
                description = 'Auszahlung'
            else:
                TransferStrategy.__log.warn("%s - Transfer; %s->???, %s, id=%s, address=%s", transaction.dateTime, transaction.mergentId, c, transaction.id, transaction.address)
                description = 'Transfer {} -> ?'.format(transaction.mergentId)
            #                                        date,                          receipt,        description, debit,                  credit,    amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
            yield     (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, self.__accounts.equity, c.account, c.amount, c.unit,   c.baseCurrency.exchangeRate, c.baseCurrency.amount, '',     c.costCenter.minus()])
            if transaction.fee.amount > 0:
                f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
                yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], '',             description, self.__accounts.fees,   c.account, f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     c.costCenter.minus()])
        self.__accountedTransferIds.add(transaction.id)

    def __transformDoubleTransfers(self, deposit, withdrawal):
        TransferStrategy.__log.debug("%s - Transfer; %s->%s, %s", withdrawal.dateTime, withdrawal.mergentId, deposit.mergentId, deposit.amount)
        description = 'Transfer {} -> {}'.format(withdrawal.mergentId, deposit.mergentId)
        d = BananaCurrency(self.__accounts, self.__currencyConverters, deposit.amount, deposit)
        w = BananaCurrency(self.__accounts, self.__currencyConverters, withdrawal.amount, withdrawal)
        if withdrawal.fee.amount > 0 and deposit.fee.amount > 0:
            TransferStrategy.__log.warn("Double transfer fees; %s, %s - %s. %s", withdrawal.mergentId, withdrawal.fee, deposit.mergentId, deposit.fee)
        # target                                    date,                         receipt,       description, deposit,              withdrawal, amount,   currency, exchangeRate,                baseCurrencyAmount,    shares, costCenter1
        yield         (deposit['bananaDate'][0],    [deposit['bananaDate'][1],    deposit.id,    description, d.account,            '',         d.amount, d.unit,   d.baseCurrency.exchangeRate, d.baseCurrency.amount, '',     d.costCenter])
        if deposit.fee.amount > 0:
            f = BananaCurrency(self.__accounts, self.__currencyConverters, deposit.fee, deposit)
            yield     (withdrawal['bananaDate'][0], [withdrawal['bananaDate'][1], '',            description, self.__accounts.fees, '',         f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])
        # source
        yield         (withdrawal['bananaDate'][0], [withdrawal['bananaDate'][1], withdrawal.id, description, '',                   w.account,  w.amount, w.unit,   w.baseCurrency.exchangeRate, w.baseCurrency.amount, '',     w.costCenter.minus()])
        if withdrawal.fee.amount > 0:
            f = BananaCurrency(self.__accounts, self.__currencyConverters, withdrawal.fee, withdrawal)
            yield     (withdrawal['bananaDate'][0], [withdrawal['bananaDate'][1], '',            description, self.__accounts.fees, f.account,  f.amount, f.unit,   f.baseCurrency.exchangeRate, f.baseCurrency.amount, '',     f.costCenter.minus()])
        self.__accountedTransferIds.add(deposit.id)
        self.__accountedTransferIds.add(withdrawal.id)
