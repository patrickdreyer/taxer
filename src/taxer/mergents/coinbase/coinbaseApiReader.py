from datetime import datetime
from pytz import utc


from ...transactions.airDrop import AirDrop
from ...transactions.buyTrade import BuyTrade
from ...transactions.currency import Currency
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.endStake import EndStake
from ...transactions.interest import Interest
from ...transactions.sellTrade import SellTrade
from ...transactions.startStake import StartStake
from ...transactions.withdrawTransfer import WithdrawTransfer
from ..reader import Reader
from .coinbaseCoinbaseAppApi import CoinbaseCoinbaseAppApi
from .coinbaseAdvancedTradeApi import CoinbaseAdvancedTradeApi


class CoinbaseApiReader(Reader):
    def __init__(self, id:str, coinbaseAppApi:CoinbaseCoinbaseAppApi, advancedTradeApi:CoinbaseAdvancedTradeApi):
        self.__id = id
        self.__coinbaseAppApi = coinbaseAppApi
        self.__advancedTradeApi = advancedTradeApi

    def read(self, year):
        yield from self.__fetchTransfers(year)
        yield from self.__fetchFills(year)

    def __fetchTransfers(self, year):
        transfers = self.__coinbaseAppApi.getTransfers()
        transfers = (self.__transformTransfers(t) for t in iter(transfers))
        for transfer in transfers:
            yield from self.__processTransfer(transfer, year)

    def __fetchFills(self, year):
        fills = self.__advancedTradeApi.getFills(year)
        fills = (self.__transformFills(t) for t in iter(fills))
        for fill in fills:
            yield from self.__processFill(fill, year)

    def __processTransfer(self, transfer, year):
        # json.dump(transfer, open(f"transaction-{transfer['type']}.json", mode='w'), default=str, indent=2)
        # yield Transaction('===', transfer['dateTime'], transfer['id'])
        if transfer['dateTime'].year != year:
            return
        if transfer['status'] != 'completed':
            return
        if transfer['type'] == 'send':
            yield from self.__processWithdrawal(transfer)
        elif transfer['type'] == 'pro_withdrawal':
            yield from self.__processDeposit(transfer)
        elif transfer['type'] == 'interest' or transfer['type'] == 'staking_reward':
            yield from self.__processInterest(transfer)
        elif transfer['type'] == 'advanced_trade_fill':
            return # ignore trades
        elif transfer['type'] == 'staking_transfer':
            yield from self.__processStartStake(transfer)
        elif transfer['type'] == 'unstaking_transfer':
            yield from self.__processEndStake(transfer)
        elif transfer['type'] == 'tx':
            yield from self.__processAirDrop(transfer)
        else:
            raise KeyError(f"Unknown transfer type; type='{transfer['type']}', transaction='{transfer['id']}'")

    def __processFill(self, fill, year):
        # json.dump(fill, open(f"fill-{fill['side']}.json", mode='w'), default=str, indent=2)
        # yield Transaction('===', fill['dateTime'], fill['trade_id'])
        if fill['dateTime'].year != year:
            return
        if fill['side'] == 'BUY':
            yield from self.__processBuy(fill)
        elif fill['side'] == 'SELL':
            yield from self.__processSell(fill)
        else:
            raise KeyError(f"Unknown fill side; side='{fill['type']}', trade='{fill['trade_id']}'")

    def __processWithdrawal(self, transfer):
        amount = Currency(transfer['amount']['currency'], transfer['amount']['amount'])
        fee = Currency(transfer['amount']['currency'], 0)
        to = transfer['to']['address'] if 'to' in transfer else None
        yield WithdrawTransfer(self.__id, transfer['dateTime'], transfer['id'], amount, fee, to)

    def __processDeposit(self, transfer):
        amount = Currency(transfer['amount']['currency'], transfer['amount']['amount'])
        fee = Currency(transfer['amount']['currency'], 0)
        yield DepositTransfer(self.__id, transfer['dateTime'], transfer['id'], amount, fee, None)

    def __processInterest(self, transfer):
        yield Interest(self.__id, transfer['dateTime'], transfer['id'], Currency(transfer['amount']['currency'], transfer['amount']['amount']))

    def __processStartStake(self, transfer):
        amount = Currency(transfer['amount']['currency'], transfer['amount']['amount'])
        fee = Currency(transfer['amount']['currency'], 0)
        yield StartStake(self.__id, transfer['dateTime'], transfer['id'], None, amount, fee)

    def __processEndStake(self, transfer):
        amount = total = Currency(transfer['amount']['currency'], transfer['amount']['amount'])
        interest = fee = Currency(transfer['amount']['currency'], 0)
        yield EndStake(self.__id, transfer['dateTime'], transfer['id'], None, amount, interest, total, fee)

    def __processAirDrop(self, transfer):
        amount = Currency(transfer['amount']['currency'], transfer['amount']['amount'])
        yield AirDrop(self.__id, transfer['dateTime'], transfer['id'], amount)

    def __processBuy(self, fill):
        symbols = fill['product_id'].split('-')
        fee = Currency(symbols[1], fill['commission'])
        buy = Currency(symbols[0], fill['size'])
        price = Currency(symbols[1], fill['price'])
        sell = Currency(symbols[1], buy.amount * price.amount)
        yield BuyTrade(self.__id, fill['dateTime'], fill['trade_id'], buy, sell, fee)

    def __processSell(self, fill):
        symbols = fill['product_id'].split('-')
        fee = Currency(symbols[1], fill['commission'])
        sell = Currency(symbols[0], fill['size'])
        price = Currency(symbols[1], fill['price'])
        buy = Currency(symbols[1], sell.amount * price.amount)
        buy -= fee
        yield SellTrade(self.__id, fill['dateTime'], fill['trade_id'], sell, buy, fee)

    def __transformTransfers(self, transfer):
        transfer['dateTime'] = utc.localize(datetime.strptime(transfer['created_at'], '%Y-%m-%dT%H:%M:%SZ'))
        if transfer['amount']['currency'] == 'ETH2':
            transfer['amount']['currency'] = 'ETH'
        return transfer

    def __transformFills(self, transfer):
        transfer['dateTime'] = utc.localize(datetime.strptime(transfer['sequence_timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ'))
        return transfer
