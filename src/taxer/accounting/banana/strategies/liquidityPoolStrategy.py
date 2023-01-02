import logging

from ....transactions.addLiquidity import AddLiquidity
from ....transactions.claimLiquidityFees import ClaimLiquidityFees
from ....transactions.createLiquidityPool import CreateLiquidityPool
from ....transactions.liquidityPool import LiquidityPool
from ....transactions.removeLiquidity import RemoveLiquidity
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class LiquidityPoolStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return issubclass(type(transaction), LiquidityPool)

    def transform(self, transaction):
        a0 = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount0, transaction)
        l0 = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount0, self.__accounts.liquidity, transaction.dateTime)
        a1 = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount1, transaction)
        l1 = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount1, self.__accounts.liquidity, transaction.dateTime)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        if isinstance(transaction, CreateLiquidityPool):
            yield from self.__transformCreateLiquidityPool(transaction, a0, l0, a1, l1, f)
        elif isinstance(transaction, AddLiquidity):
            yield from self.__transformAddLiquidity(transaction, a0, l0, a1, l1, f)
        elif isinstance(transaction, ClaimLiquidityFees):
            yield from self.__transformClaimLiquidityFees(transaction, a0, l0, a1, l1, f)
        elif isinstance(transaction, RemoveLiquidity):
            yield from self.__transformRemoveLiquidity(transaction, a0, l0, a1, l1, f)
        else:
            LiquidityPoolStrategy.__log.error("Unknown liquidity pool transaction; class='%s'", type(transaction).__name__)
            raise ValueError("Unknown liquidity pool transaction; type='{}'".format(type(transaction)))

    def __transformCreateLiquidityPool(self, transaction, a0, l0, a1, l1, f):
        LiquidityPoolStrategy.__log.debug("%s - Provide liquidity; %s, %s/%s", transaction.dateTime, transaction.poolId, a0, a1)
        description = f"Liquidität bereit stellen; {transaction.poolId}: {transaction.amount0.unit}/{transaction.amount1.unit}"
        # withdrawal0                                     description, debit,                credit,     amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares, costCenter1
        yield BananaStrategy._createBooking(transaction, [description, '',                   a0.account, a0.amount, a0.unit,  a0.baseCurrency.exchangeRate, a0.baseCurrency.amount, '',     a0.costCenter.minus()])
        # liquidity0
        yield BananaStrategy._createBooking(transaction, [description, l0.account,           '',         l0.amount, l0.unit,  l0.baseCurrency.exchangeRate, a0.baseCurrency.amount, '',     l0.costCenter])
        # withdrawal1
        yield BananaStrategy._createBooking(transaction, [description, '',                   a1.account, a1.amount, a1.unit,  a1.baseCurrency.exchangeRate, a1.baseCurrency.amount, '',     l1.costCenter.minus()])
        # liquidity1
        yield BananaStrategy._createBooking(transaction, [description, l1.account,           '',         l1.amount, l1.unit,  l1.baseCurrency.exchangeRate, a1.baseCurrency.amount, '',     l1.costCenter])
        # fee
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.fees, f.account,  f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  '',     f.costCenter.minus()])

    def __transformAddLiquidity(self, transaction, a0, l0, a1, l1, f):
        LiquidityPoolStrategy.__log.debug("%s - Add liquidity; %s, %s/%s", transaction.dateTime, transaction.poolId, a0, a1)
        description = f"Liquidität erhöhen; {transaction.poolId}: {transaction.amount0.unit}/{transaction.amount1.unit}"
        # withdrawal0                                     description, debit,                credit,     amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares, costCenter1
        yield BananaStrategy._createBooking(transaction, [description, '',                   a0.account, a0.amount, a0.unit,  a0.baseCurrency.exchangeRate, a0.baseCurrency.amount, '',     a0.costCenter.minus()])
        # liquidity0
        yield BananaStrategy._createBooking(transaction, [description, l0.account,           '',         l0.amount, l0.unit,  l0.baseCurrency.exchangeRate, a0.baseCurrency.amount, '',     l0.costCenter])
        # withdrawal1
        yield BananaStrategy._createBooking(transaction, [description, '',                   a1.account, a1.amount, a1.unit,  a1.baseCurrency.exchangeRate, a1.baseCurrency.amount, '',     l1.costCenter.minus()])
        # liquidity1
        yield BananaStrategy._createBooking(transaction, [description, l1.account,           '',         l1.amount, l1.unit,  l1.baseCurrency.exchangeRate, a1.baseCurrency.amount, '',     l1.costCenter])
        # fee
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.fees, f.account,  f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  '',     f.costCenter.minus()])

    def __transformClaimLiquidityFees(self, transaction, a0, l0, a1, l1, f):
        LiquidityPoolStrategy.__log.debug("%s - Claim liquidity fees; %s, %s/%s", transaction.dateTime, transaction.poolId, a0, a1)
        description = f"Liquiditätsgebühren einziehen; {transaction.poolId}: {transaction.amount0.unit}/{transaction.amount1.unit}"
        # amount0                                         description, debit,                credit,                 amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares, costCenter1
        yield BananaStrategy._createBooking(transaction, [description, a0.account,           self.__accounts.equity, a0.amount, a0.unit,  a0.baseCurrency.exchangeRate, a0.baseCurrency.amount, '',     a0.costCenter])
        # amount1
        yield BananaStrategy._createBooking(transaction, [description, a1.account,           self.__accounts.equity, a1.amount, a1.unit,  a1.baseCurrency.exchangeRate, a1.baseCurrency.amount, '',     a1.costCenter])
        # fee
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.fees, f.account,              f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  '',     f.costCenter.minus()])

    def __transformRemoveLiquidity(self, transaction, a0, l0, a1, l1, f):
        LiquidityPoolStrategy.__log.debug("%s - Remove liquidity; %s, %s/%s", transaction.dateTime, transaction.poolId, a0, a1)
        description = f"Liquidität auflösen; {transaction.poolId}: {transaction.amount0.unit}/{transaction.amount1.unit}"
        # deposit0                                        description, debit,                credit,     amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares, costCenter1
        yield BananaStrategy._createBooking(transaction, [description, a0.account,           '',         a0.amount, a0.unit,  a0.baseCurrency.exchangeRate, a0.baseCurrency.amount, '',     a0.costCenter])
        # liquidity0
        yield BananaStrategy._createBooking(transaction, [description, '',                   l0.account, l0.amount, l0.unit,  l0.baseCurrency.exchangeRate, a0.baseCurrency.amount, '',     l0.costCenter.minus()])
        # deposit1
        yield BananaStrategy._createBooking(transaction, [description, a1.account,           '',         a1.amount, a1.unit,  a1.baseCurrency.exchangeRate, a1.baseCurrency.amount, '',     l1.costCenter])
        # liquidity1
        yield BananaStrategy._createBooking(transaction, [description, '',                   l1.account, l1.amount, l1.unit,  l1.baseCurrency.exchangeRate, a1.baseCurrency.amount, '',     l1.costCenter.minus()])
        # fee
        yield BananaStrategy._createBooking(transaction, [description, self.__accounts.fees, f.account,  f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  '',     f.costCenter.minus()])
