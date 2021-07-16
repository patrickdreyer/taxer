import datetime
import json
import os
import requests
import pytz

from .hexFileReader import HEXFileReader
from .tokenFunctionDecoder import TokenFunctionDecoder
from ..reader import Reader
from ...transactions.currency import Currency
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.withdrawTransfer import WithdrawTransfer
from ...transactions.enterLobby import EnterLobby
from ...transactions.exitLobby import ExitLobby
from ...transactions.startStake import StartStake
from ...transactions.endStake import EndStake


class EtherscanApiReader(Reader):
    __apiUrl = 'https://api.etherscan.io/api'
    __divisor = 1000000000000000000

    def __init__(self, config, inputPath, cachePath):
        for account in config['accounts']:
            account['address'] = account['address'].lower()
        for token in config['tokens']:
            token['address'] = token['address'].lower()
        self.__config = config
        self.__tokenFunctionDecoder = TokenFunctionDecoder.create(config, cachePath)
        self.__tokenTransactions = dict()
        self.__hexFileReader = HEXFileReader(inputPath)

    def read(self, year):
        self.__year = year
        self.__hexTransformations = list(self.__hexFileReader.read(self.__year))
        with requests.Session() as self.__session:
            for account in self.__config['accounts']:
                yield from self.__fetchNormalTransactions(year, account)
                yield from self.__fetchERC20Transactions(year, account)

    def __fetchNormalTransactions(self, year, account):
        response = self.__session.get('{}?module=account&action=txlist&address={}&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc&apikey={}'.format(EtherscanApiReader.__apiUrl, account['address'], self.__config['apiKeyToken']))
        content = json.loads(response.content)
        transactions = map(self.__transformTransaction, content['result'])
        filteredErrors = filter(self.__filterErrors, transactions)
        filteredYear = filter(self.__filterWrongYear, filteredErrors)
        for transaction in filteredYear:
            amount = Currency('ETH', float(transaction['value']) / EtherscanApiReader.__divisor)
            fee = EtherscanApiReader.__fee(transaction)
            if transaction['function'] == 'xflobbyenter':
                yield EnterLobby(account['id'], transaction['dateTime'], transaction['hash'], amount, fee, transaction['to'])
            elif (transaction['function'] == 'xflobbyexit'
                or transaction['function'] == 'stakestart'
                or transaction['function'] == 'stakeend'):
                self.__tokenTransactions[transaction['hash']] = transaction
            elif transaction['from'] == account['address']:
                yield WithdrawTransfer(account['id'], transaction['dateTime'], transaction['hash'], amount, fee)
            elif transaction['to'] == account['address']:
                amount = amount - fee
                yield DepositTransfer(account['id'], transaction['dateTime'], transaction['hash'], amount, fee)

    def __fetchERC20Transactions(self, year, account):
        for token in self.__config['tokens']:
            response = self.__session.get('{}?module=account&action=tokentx&address={}&contractaddress={}&page=1&offset=100&sort=asc&apikey={}'.format(EtherscanApiReader.__apiUrl, account['address'], token['address'], self.__config['apiKeyToken']))
            content = json.loads(response.content)
            transactions = map(self.__transformTransaction, content['result'])
            filteredYear = list(filter(self.__filterWrongYear, transactions))
            for transaction in filteredYear:
                if not transaction['hash'] in self.__tokenTransactions:
                    continue
                tokenTransaction = self.__tokenTransactions[transaction['hash']]
                fee = EtherscanApiReader.__fee(tokenTransaction)
                amount = Currency(token['id'], float(transaction['value']) / float('1' + '0'*int(transaction['tokenDecimal'])))
                if tokenTransaction['function'] == 'xflobbyexit':
                    hexTransformation = [t for t in self.__hexTransformations if t['HEX'] == int(amount.amount)][0]
                    lobby = Currency('ETH', hexTransformation['ETH'])
                    yield ExitLobby(account['id'], tokenTransaction['dateTime'], tokenTransaction['hash'], lobby, amount, fee)
                elif tokenTransaction['function'] == 'stakestart':
                    yield StartStake(account['id'], tokenTransaction['dateTime'], tokenTransaction['hash'], amount, fee)
                elif tokenTransaction['function'] == 'stakeend':
                    yield EndStake(account['id'], tokenTransaction['dateTime'], tokenTransaction['hash'], amount, fee)
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
        return address in [token['address'] for token in self.__config['tokens']]

    def __getTokenId(self, address):
        return [token for token in self.__config['tokens'] if token['address'] == address][0]['id']

    @staticmethod
    def __fee(transaction):
        return Currency('ETH', float(transaction['gasUsed']) * float(transaction['gasPrice']) / EtherscanApiReader.__divisor)
