import datetime
from decimal import Decimal
import json
import requests
import pytz

from .tokenFunctionDecoder import TokenFunctionDecoder
from ..reader import Reader
from ...transactions.currency import Currency
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.cancelFee import CancelFee
from ...transactions.withdrawTransfer import WithdrawTransfer
from ...transactions.enterLobby import EnterLobby
from ...transactions.exitLobby import ExitLobby
from ...transactions.startStake import StartStake
from ...transactions.endStake import EndStake


class EtherscanApiReader(Reader):
    __apiUrl = 'https://api.etherscan.io/api'
    __divisor = 1000000000000000000

    def __init__(self, config, cachePath, hexReader):
        config['accounts'] = {k.lower():v for k,v in config['accounts'].items()}
        config['tokens'] = {k.lower():v for k,v in config['tokens'].items()}
        self.__config = config
        self.__tokenFunctionDecoder = TokenFunctionDecoder.create(config, cachePath, EtherscanApiReader.__apiUrl)
        self.__tokenTransactions = dict()
        self.__hexReader = hexReader

    def read(self, year):
        self.__year = year
        with requests.Session() as self.__session:
            for address,id in self.__config['accounts'].items():
                yield from self.__fetchNormalTransactions(year, address, id)
                yield from self.__fetchERC20Transactions(year, address, id)

    def __fetchNormalTransactions(self, year, address, id):
        response = self.__session.get('{}?module=account&action=txlist&address={}&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc&apikey={}'.format(EtherscanApiReader.__apiUrl, address, self.__config['apiKeyToken']))
        content = json.loads(response.content)
        transactions = map(self.__transformTransaction, content['result'])
        filteredErrors = filter(self.__filterErrors, transactions)
        filteredYear = filter(self.__filterWrongYear, filteredErrors)
        for transaction in filteredYear:
            amount = Currency('ETH', Decimal(transaction['value']) / EtherscanApiReader.__divisor)
            fee = EtherscanApiReader.__fee(transaction)
            if transaction['function'] == 'xflobbyenter':
                yield EnterLobby(id, transaction['dateTime'], transaction['hash'], amount, fee, transaction['to'])
            elif (transaction['function'] == 'xflobbyexit'
                or transaction['function'] == 'stakestart'
                or transaction['function'] == 'stakeend'):
                self.__tokenTransactions[transaction['hash']] = transaction
            elif transaction['from'] == address and transaction['to'] == address:
                yield CancelFee(id, transaction['dateTime'], transaction['hash'], fee)
            elif transaction['from'] == address:
                yield WithdrawTransfer(id, transaction['dateTime'], transaction['hash'], amount, fee)
            elif transaction['to'] == address:
                yield DepositTransfer(id, transaction['dateTime'], transaction['hash'], amount, Currency('ETH', 0))
            else:
                pass

    def __fetchERC20Transactions(self, year, address, id):
        for tokenAddress,tokenId in self.__config['tokens'].items():
            response = self.__session.get('{}?module=account&action=tokentx&address={}&contractaddress={}&page=1&offset=100&sort=asc&apikey={}'.format(EtherscanApiReader.__apiUrl, address, tokenAddress, self.__config['apiKeyToken']))
            content = json.loads(response.content)
            transactions = map(self.__transformTransaction, content['result'])
            filteredYear = list(filter(self.__filterWrongYear, transactions))
            for transaction in filteredYear:
                if not transaction['hash'] in self.__tokenTransactions:
                    continue
                tokenTransaction = self.__tokenTransactions[transaction['hash']]
                fee = EtherscanApiReader.__fee(tokenTransaction)
                amount = Currency(tokenId, Decimal(transaction['value']) / Decimal('1' + '0'*int(transaction['tokenDecimal'])))
                if tokenTransaction['function'] == 'xflobbyexit':
                    lobby = self.__getETHForHEX(amount.amount)
                    yield ExitLobby(id, tokenTransaction['dateTime'], tokenTransaction['hash'], lobby, amount, fee)
                elif tokenTransaction['function'] == 'stakestart':
                    yield StartStake(id, tokenTransaction['dateTime'], tokenTransaction['hash'], amount, fee)
                elif tokenTransaction['function'] == 'stakeend':
                    principal = self.__getHEXStakePrincipal(amount.amount)
                    interest = amount - principal
                    yield EndStake(id, tokenTransaction['dateTime'], tokenTransaction['hash'], principal, interest, amount, fee)
                else:
                    pass

    def __transformTransaction(self, transaction):
        transaction['dateTime'] = pytz.utc.localize(datetime.datetime.fromtimestamp(int(transaction['timeStamp'])))
        if self.__isToken(transaction['from']):
            transaction['function'] = self.__tokenFunctionDecoder.decode(transaction['from'], transaction['input']).lower()
            transaction['from'] = self.__getTokenId(transaction['from'])
        elif self.__isToken(transaction['to']):
            transaction['function'] = self.__tokenFunctionDecoder.decode(transaction['to'], transaction['input']).lower()
            transaction['to'] = self.__getTokenId(transaction['to'])
        else:
            transaction['function'] = ''
        return transaction

    def __filterErrors(self, transaction):
        return transaction['isError'] == '0'

    def __filterWrongYear(self, transaction):
        return transaction['dateTime'].year == self.__year

    def __isToken(self, address):
        return address in [token for token in self.__config['tokens']]

    def __getTokenId(self, address):
        return [v for k,v in self.__config['tokens'].items() if k == address][0]

    def __getETHForHEX(self, hex):
        hex = int(hex)
        transformation = [t for t in self.__hexReader.transformed if t.hex == hex][0]
        return Currency('ETH', transformation.eth)

    def __getHEXStakePrincipal(self, total):
        total = int(total)
        stake = [s for s in self.__hexReader.history if s.total == total][0]
        return Currency('HEX', stake.principal)

    @staticmethod
    def __fee(transaction):
        return Currency('ETH', Decimal(transaction['gasUsed']) * Decimal(transaction['gasPrice']) / EtherscanApiReader.__divisor)
