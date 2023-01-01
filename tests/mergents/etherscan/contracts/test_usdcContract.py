from datetime import datetime
from pytest import fixture, raises

from taxer.mergents.etherscan.contracts.usdcContract import UsdcContract


class TestUsdcContract:
    @fixture
    def mockEtherscanApi(self, mocker):
        return mocker.patch('taxer.mergents.etherscan.etherscanApi.EtherscanApi.getContract', return_value = None)

    @fixture
    def testee(self, mockEtherscanApi):
        return UsdcContract(None, mockEtherscanApi)

    def test_processTransaction_sameYear_exception(self, testee):
        # arrange
        transaction = {}
        transaction['dateTime'] = datetime(2021, 1, 1)

        # act & assert
        with raises(NotImplementedError):
            list(testee.processTransaction('ADDRESS', 'ID', 2021, transaction, None))

    def test_processTransaction_differentYear_emptyGenerator(self, testee):
        # arrange
        transaction = {}
        transaction['dateTime'] = datetime(2022, 1, 1)

        # act
        actual = list(testee.processTransaction('ADDRESS', 'ID', 2021, transaction, None))

        # assert
        assert len(actual) == 0
