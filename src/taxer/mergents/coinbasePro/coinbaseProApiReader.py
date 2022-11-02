from datetime import datetime
from dateutil import parser
from pytz import utc

from ..reader import Reader
from ...transactions.buyTrade import BuyTrade
from ...transactions.currency import Currency
from ...transactions.sellTrade import SellTrade
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.withdrawTransfer import WithdrawTransfer


class CoinbaseProApiReader(Reader):
    def __init__(self, config, api):
        self.__config = config
        self.__api = api

    def read(self, year):
        accounts = self.__api.getAllAccounts()
        if len(accounts) == 0:
            return

        profileId = accounts[0]['profile_id']
        yield from self.__fetchTransfers(profileId, accounts, year)
        yield from self.__fetchFills(profileId, accounts, year)

    def __fetchTransfers(self, profileId, accounts, year):
        transfers = self.__api.getAllTransfers(profileId)
        transfers = (self.__transformTransfers(accounts, t) for t in iter(transfers))
        for transfer in transfers:
            if transfer['type'] == 'withdraw':
                if transfer['dateTime'].year != year:
                    continue
                fee = Currency(transfer['currency'], 0)
                # even if fee is given in transfer, CBP does not deduce it
                # if 'fee' in transfer['details']:
                #     fee = Currency(transfer['currency'], transfer['details']['fee'])
                yield WithdrawTransfer(self.__config['id'], transfer['dateTime'], transfer['id'], Currency(transfer['currency'], transfer['amount']), fee)
            elif transfer['type'] == 'deposit':
                if transfer['dateTime'].year != year:
                    continue
                fee = Currency(transfer['currency'], 0)
                if 'fee' in transfer['details']:
                    fee = Currency(transfer['currency'], transfer['details']['fee'])
                yield DepositTransfer(self.__config['id'], transfer['dateTime'], transfer['id'], Currency(transfer['currency'], transfer['amount']), fee)

    def __fetchFills(self, profileId, accounts, year):
        fills = self.__api.getAllFills(profileId)
        for fill in fills:
            date = parser.isoparse(fill['created_at'])
            if date.year != year:
                continue
            symbols = fill['product_id'].split('-')
            fee = Currency(symbols[1], fill['fee'])
            symbol1 = Currency(symbols[0], fill['size'])
            price = Currency(symbols[1], fill['price'])
            symbol2 = Currency(symbols[1], symbol1.amount * price.amount)
            if fill['side'] == 'sell':
                symbol2 -= fee
                yield SellTrade(self.__config['id'], date, fill['order_id'], symbol1, symbol2, fee)
            elif fill['side'] == 'buy':
                yield BuyTrade(self.__config['id'], date, fill['order_id'], symbol1, symbol2, fee)

    def __transformTransfers(self, accounts, transfer):
        transfer['currency'] = [a['currency'] for a in accounts if a['id'] == transfer['account_id']][0]
        transfer['dateTime'] = utc.localize(datetime.strptime(transfer['completed_at'].replace('+00', ''), '%Y-%m-%d %H:%M:%S.%f'))
        return transfer
