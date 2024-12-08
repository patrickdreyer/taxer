import json
import os
import requests
import web3

from ...throttler import Throttler


class EtherscanApi:
    __offset = 1000
    __throttler = Throttler(5)

    def __init__(self, url:str, keyToken:str, cache:str):
        self.__url = url
        self.__keyToken = keyToken
        self.__cache = cache
        self.__web3 = web3.Web3()
        self.__session = requests.Session()

    def __del__(self):
        self.__session.close()

    def getNormalTransactions(self, address):
        yield from self.__getTransactions(lambda page : '{}?module=account&action=txlist&address={}&startblock=0&endblock=99999999&page={}&offset={}&sort=asc&apikey={}'.format(self.__url, address, page, EtherscanApi.__offset, self.__keyToken))

    def getErc20Transactions(self, address):
        yield from self.__getTransactions(lambda page : '{}?module=account&action=tokentx&address={}&page={}&offset={}&sort=asc&apikey={}'.format(self.__url, address, page, EtherscanApi.__offset, self.__keyToken))

    def getInternalTransactions(self, transactionHash):
        query = '{}?module=account&action=txlistinternal&txhash={}&apikey={}'.format(self.__url, transactionHash, self.__keyToken)
        self.__throttler.throttle()
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['result']

    def __getTransactions(self, queryFunc):
        page = 1
        while True:
            query = queryFunc(page)
            self.__throttler.throttle()
            response = self.__session.get(query)
            content = json.loads(response.content)
            if not content['result']:
                return
            for i in content['result']:
                yield i
            page += 1

    # https://github.com/ethereum/web3.py/blob/v4.9.1/docs/contracts.rst#utils
    def getContract(self, address):
        abi = self.getContractAbi(address)
        if abi == None:
            return None
        contract = self.__web3.eth.contract(address=self.__web3.to_checksum_address(address), abi=abi)
        return contract

    def getContractAbi(self, contractAddress):
        filePath = os.path.join(self.__cache, '{}.abi'.format(contractAddress))
        if os.path.isfile(filePath):
            with open(filePath, 'r') as file:
                return file.read()
        self.__throttler.throttle()
        response = self.__session.get('{}?module=contract&action=getabi&address={}&apikey={}'.format(self.__url, contractAddress, self.__keyToken))
        content = json.loads(response.content)
        if content['message'] == 'NOTOK':
            return None
        with open(filePath, 'w') as file:
            file.write(content['result'])
        return content['result']

    def getLogs(self, block, *, address = None, topic0 = None, topic1 = None, topic2 = None):
        params = []
        if address:
            params.append(f"address={address}")
        if topic0:
            params.append(f"topic0={topic0}")
        if topic1:
            params.append(f"topic1={topic1}")
        if topic2:
            params.append(f"topic2={topic2}")
        if topic0 and topic1:
            params.append('topic0_1_opr=and')
        params = str.join('&', params)
        query = f"{self.__url}?module=logs&action=getLogs&fromBlock={block}&toBlock={block}&{params}&apikey={self.__keyToken}"
        self.__throttler.throttle()
        response = self.__session.get(query)
        content = json.loads(response.content)
        if content['message'] == 'NOTOK':
            raise Exception(content['result'])
        return content['result']

    def getFirstLog(self, block, *, address = None, topic0 = None, topic1 = None, topic2 = None):
        logs = self.getLogs(block, address = address, topic0 = topic0, topic1 = topic1, topic2 = topic2)
        return logs[0]
