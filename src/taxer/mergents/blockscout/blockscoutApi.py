import json
import logging
import os
import requests
import web3

from ...throttler import Throttler


# https://api.scan.pulsechain.com/api-docs
class BlockscoutApi:
    def __init__(self, url:str, cache:str):
        self.__log = logging.getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))
        self.__url = url
        self.__cache = cache
        self.__web3 = web3.Web3()
        self.__session = requests.Session()

    def __del__(self):
        self.__session.close()

    def getTokens(self, address):
        response = self.__session.get(f"{self.__url}/addresses/{address}/tokens?type=ERC-20%2CERC-721%2CERC-1155")
        content = json.loads(response.content)
        return [t['token']['address'] for t in content['items']]

    def getNormalTransactions(self, address):
        yield from self.__getTransactions(f"{self.__url}/addresses/{address}/transactions")

    def getErc20Transaction(self, transactionHash):
        return next(self.__getTransactions(f"{self.__url}/transactions/{transactionHash}/token-transfers?type=ERC-20%2CERC-721%2CERC-1155"), None)

    def getInternalTransactions(self, transactionHash):
        yield from self.__getTransactions(f"{self.__url}/transactions/{transactionHash}/internal-transactions")

    def __getTransactions(self, query):
        response = self.__session.get(query)
        if response.status_code != 200:
            return
        content = json.loads(response.content)
        if not content['items']:
            return
        for i in content['items']:
            yield i

    # https://github.com/ethereum/web3.py/blob/v4.9.1/docs/contracts.rst#utils
    def getContract(self, address):
        abi = self.getContractAbi(address)
        if not abi:
            return None
        contract = self.__web3.eth.contract(address=self.__web3.toChecksumAddress(address), abi=abi)
        return contract

    def getContractAbi(self, contractAddress):
        filePath = os.path.join(self.__cache, 'PulseChain_{}.abi'.format(contractAddress))
        if os.path.isfile(filePath):
            with open(filePath, 'r') as file:
                return file.read()
        smartContract = self.getSmartContract(contractAddress)
        if not smartContract['abi']:
            return None
        with open(filePath, 'w') as file:
            file.write(json.dumps(smartContract['abi']))
        return smartContract['abi']

    def getSmartContract(self, address):
        query = f"{self.__url}/smart-contracts/{address}"
        response = self.__session.get(query)
        if response.status_code != 200:
            self.__log.error("API error; query='%s', status_code=%s, reason='%s'", query, response.status_code, response.reason)
            return {'name': None, 'abi': None}
        content = json.loads(response.content)
        if not 'name' in content:
            content['name'] = None
        if not 'abi' in content:
            content['abi'] = None
        return content

    def getLogs(self, address, *, topic0 = None, topic1 = None, topic2 = None):
        response = self.__session.get(f"{self.__url}/transactions/{address}/logs")
        if response.status_code != 200:
            raise Exception(response.reason)
        content = json.loads(response.content)
        ret = []
        for i in content['items']:
            if topic0 and i['topics'][0].lower() != topic0.lower():
                continue
            if topic1 and i['topics'][1].lower() != topic1.lower():
                continue
            if topic2 and i['topics'][2].lower() != topic2.lower():
                continue
            ret.append(i)
        return ret

    def getFirstLog(self, block, *, address = None, topic0 = None, topic1 = None, topic2 = None):
        logs = self.getLogs(block, address = address, topic0 = topic0, topic1 = topic1, topic2 = topic2)
        return logs[0]
