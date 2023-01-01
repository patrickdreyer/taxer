import json
import os
import web3

from ...throttler import Throttler


class EtherscanApi:
    __offset = 1000
    __throttler = Throttler(5)

    def __init__(self, config, cachePath, session):
        self.__config = config
        self.__cachePath = cachePath
        self.__session = session
        self.__web3 = web3.Web3()


    def getNormalTransactions(self, address):
        yield from self.__getTransactions(lambda page : '{}?module=account&action=txlist&address={}&startblock=0&endblock=99999999&page={}&offset={}&sort=asc&apikey={}'.format(self.__config['apiUrl'], address, page, EtherscanApi.__offset, self.__config['apiKeyToken']))

    def getErc20Transactions(self, address):
        yield from self.__getTransactions(lambda page : '{}?module=account&action=tokentx&address={}&page={}&offset={}&sort=asc&apikey={}'.format(self.__config['apiUrl'], address, page, EtherscanApi.__offset, self.__config['apiKeyToken']))

    def getInternalTransactions(self, transactionHash):
        query = '{}?module=account&action=txlistinternal&txhash={}&apikey={}'.format(self.__config['apiUrl'], transactionHash, self.__config['apiKeyToken'])
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
        contract = self.__web3.eth.contract(address=self.__web3.toChecksumAddress(address), abi=abi)
        return contract

    def getContractAbi(self, contractAddress):
        filePath = os.path.join(self.__cachePath, '{}.abi'.format(contractAddress))
        if os.path.isfile(filePath):
            with open(filePath, 'r') as file:
                return file.read()
        self.__throttler.throttle()
        response = self.__session.get('{}?module=contract&action=getabi&address={}&apikey={}'.format(self.__config['apiUrl'], contractAddress, self.__config['apiKeyToken']))
        content = json.loads(response.content)
        if content['message'] == 'NOTOK':
            return None
        with open(filePath, 'w') as file:
            file.write(content['result'])
        return content['result']

    def getLogs(self, block, address, topic0, fromAddress):
        topic1 = '0x{:0>64}'.format(fromAddress[2:])
        query = '{}?module=logs&action=getLogs&fromBlock={}&toBlock={}&address={}&topic0={}&topic0_1_opr=and&topic1={}&apikey={}'.format(self.__config['apiUrl'], block, block, address, topic0, topic1, self.__config['apiKeyToken'])
        self.__throttler.throttle()
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['result']

    def getLogsByTopic(self, block, address, topic0):
        query = f"{self.__config['apiUrl']}?module=logs&action=getLogs&fromBlock={block}&toBlock={block}&address={address}&topic0={topic0}&apikey={self.__config['apiKeyToken']}"
        self.__throttler.throttle()
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['result']

    def getLogsByTopic1(self, block, topic1):
        query = f"{self.__config['apiUrl']}?module=logs&action=getLogs&fromBlock={block}&toBlock={block}&topic1={topic1}&apikey={self.__config['apiKeyToken']}"
        self.__throttler.throttle()
        response = self.__session.get(query)
        content = json.loads(response.content)
        if content['message'] == 'NOTOK':
            raise Exception(content['result'])
        return content['result']

    def getLogsByTopic2(self, block, topic2):
        query = f"{self.__config['apiUrl']}?module=logs&action=getLogs&fromBlock={block}&toBlock={block}&topic2={topic2}&apikey={self.__config['apiKeyToken']}"
        self.__throttler.throttle()
        response = self.__session.get(query)
        content = json.loads(response.content)
        if content['message'] == 'NOTOK':
            raise Exception(content['result'])
        return content['result']

    def getPublicNameTagByAddress(self, address):
        return self.__config['publicNameTags'][address] if address in self.__config['publicNameTags'] else None
