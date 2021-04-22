import datetime
from  dateutil import parser
import hashlib
import hmac
import json
import os
import requests
import web3


from ..reader import Reader
from ...transactions.sellTrade import SellTrade
from ...transactions.buyTrade import BuyTrade
from ...transactions.withdrawTransfer import WithdrawTransfer


class EtherscanApiReader(Reader):
    __apiUrl = 'https://api.etherscan.io/api'

    def __init__(self, config, cachePath):
        self.__config = config
        self.__tokenContracts = EtherscanApiReader.__createTokenContracts(config['tokens'], config['apiKeyToken'], cachePath)

    def read(self, year):
        for address in self.__config['addresses']:
            with open('etherscan.txt', 'w') as self.file:
                self.__fetchNormalTransactions(year, address)
                self.__fetchInternalTransactions(year, address)
                self.__fetchERC20Transactions(year, address)
                # yield from self.__fetchERC721Transactions(year, address)
        raise Exception('TODO')

    @staticmethod
    def __createTokenContracts(tokens, apiKeyToken, cachePath):
        ret = {}
        w3 = web3.Web3()
        for token in tokens:
            abi = EtherscanApiReader.__fetchContractAbi(token['address'], apiKeyToken, cachePath)
            contract = w3.eth.contract(address=w3.toChecksumAddress(token['address']), abi=abi)
            ret[token['address']] = contract
        return ret

    @staticmethod
    def __fetchContractAbi(contractAddress, etherscanApiKeyToken, cachePath):
        filePath = os.path.join(cachePath, '{}.abi'.format(contractAddress))
        if os.path.isfile(filePath):
            with open(filePath, 'r') as file:
                return file.read()
        response = requests.get('{}?module=contract&action=getabi&address={}&apikey={}'.format(EtherscanApiReader.__apiUrl, contractAddress, etherscanApiKeyToken))
        content = json.loads(response.content)
        abi = content['result']
        with open(filePath, 'w') as file:
            file.write(abi)
        return abi

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
        if transaction['from'] in self.__tokenContracts:
            contractAddress = transaction['from']
        elif transaction['to'] in self.__tokenContracts:
            contractAddress = transaction['to']
        else:
            return transaction['input']
        contract = self.__tokenContracts[contractAddress]
        try:
            ret = contract.decode_function_input(transaction['input'])
            return ret[0].fn_name
        except:
            return transaction['input']
