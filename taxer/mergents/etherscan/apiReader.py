import json
import os
import requests


from .tokenFunctionDecoder import TokenFunctionDecoder
from ..reader import Reader
from ...transactions.sellTrade import SellTrade
from ...transactions.buyTrade import BuyTrade
from ...transactions.withdrawTransfer import WithdrawTransfer


class EtherscanApiReader(Reader):
    __apiUrl = 'https://api.etherscan.io/api'

    def __init__(self, config, cachePath):
        self.__config = config
        self.__tokenFunctionDecoder = TokenFunctionDecoder.create(config, cachePath)

    def read(self, year):
        for address in self.__config['addresses']:
            with open('etherscan.txt', 'w') as self.file:
                self.__fetchNormalTransactions(year, address)
                self.__fetchInternalTransactions(year, address)
                self.__fetchERC20Transactions(year, address)
                # yield from self.__fetchERC721Transactions(year, address)
        raise Exception('TODO')

    def __fetchNormalTransactions(self, year, address):
        response = requests.get('{}?module=account&action=txlist&address={}&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc&apikey={}'.format(EtherscanApiReader.__apiUrl, address, self.__config['apiKeyToken']))
        content = json.loads(response.content)
        transactions = content['result']
        self.file.write('Normal Transactions\n')
        self.file.write('===================\n')
        for transaction in transactions:
            transaction['input'] = self.__decodeFunction(transaction)
            self.file.write(json.dumps(transaction))
            self.file.write('\n')

    def __fetchInternalTransactions(self, year, address):
        response = requests.get('{}?module=account&action=txlistinternal&address={}&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc&apikey={}'.format(EtherscanApiReader.__apiUrl, address, self.__config['apiKeyToken']))
        content = json.loads(response.content)
        transactions = content['result']
        self.file.write('Internal Transactions\n')
        self.file.write('=====================\n')
        for transaction in transactions:
            transaction['input'] = self.__decodeFunction(transaction)
            self.file.write(json.dumps(transaction))
            self.file.write('\n')

    def __fetchERC20Transactions(self, year, address):
        for token in self.__config['tokens']:
            response = requests.get('{}?module=account&action=tokentx&contractaddress={}&address={}&page=1&offset=100&sort=asc&apikey={}'.format(EtherscanApiReader.__apiUrl, token['address'], address, self.__config['apiKeyToken']))
            content = json.loads(response.content)
            transactions = content['result']
            self.file.write('ERC20 Transactions {}\n'.format(token['name']))
            self.file.write('======================\n')
            for transaction in transactions:
                transaction['input'] = self.__decodeFunction(transaction)
                self.file.write(json.dumps(transaction))
                self.file.write('\n')

    # https://github.com/ethereum/web3.py/blob/v4.9.1/docs/contracts.rst#utils
    def __decodeFunction(self, transaction):
        if self.__tokenFunctionDecoder.isContractAddress(transaction['from']):
            contractAddress = transaction['from']
        elif self.__tokenFunctionDecoder.isContractAddress(transaction['to']):
            contractAddress = transaction['to']
        else:
            return transaction['input']
        return self.__tokenFunctionDecoder.decode(contractAddress, transaction['input'])
