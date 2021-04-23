import json
import os
import requests
import web3


class TokenFunctionDecoder():
    @staticmethod
    def create(config, cachePath):
        tokenContracts = TokenFunctionDecoder.__createTokenContracts(config['tokens'], config['apiKeyToken'], cachePath)
        return TokenFunctionDecoder(tokenContracts)
        
    def __init__(self, tokenContracts):
        self.__tokenContracts = tokenContracts

    def isContractAddress(self, address):
        return address in self.__tokenContracts

    def decode(self, contractAddress, input):
        contract = self.__tokenContracts[contractAddress]
        try:
            ret = contract.decode_function_input(input)
            return ret[0].fn_name
        except:
            return input

    @staticmethod
    def __createTokenContracts(tokens, apiKeyToken, cachePath):
        ret = {}
        w3 = web3.Web3()
        for token in tokens:
            abi = TokenFunctionDecoder.__fetchContractAbi(token['address'], apiKeyToken, cachePath)
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
