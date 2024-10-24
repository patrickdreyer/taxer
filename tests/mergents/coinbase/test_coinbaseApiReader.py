from decimal import Decimal
from pytest import fixture, mark, raises

from taxer.mergents.coinbase.coinbaseApiReader import CoinbaseApiReader
from taxer.transactions.airDrop import AirDrop
from taxer.transactions.buyTrade import BuyTrade
from taxer.transactions.endStake import EndStake
from taxer.transactions.interest import Interest
from taxer.transactions.sellTrade import SellTrade
from taxer.transactions.startStake import StartStake
from taxer.transactions.transaction import Transaction
from taxer.transactions.withdrawTransfer import WithdrawTransfer
from tests.testData import TestData


class TestCoinbaseApiReader:
    @fixture
    def testee(self):
        return CoinbaseApiReader('===', None, None)

    #region Transactions

    @mark.parametrize("fileName", [
        ('transaction-pro_withdrawal'),
    ])
    def test_processTransfer_2023MinusTransferType_Skip(self, testee: CoinbaseApiReader, fileName:str):
        # arrange
        transfer = self.__loadTransaction(testee, fileName)

        # act
        actual = [*testee._CoinbaseApiReader__processTransfer(transfer, 2024)]

        # assert
        assert len(actual) == 0


    def test_processTransfer_BeforeYear_Skip(self, testee: CoinbaseApiReader):
        # arrange
        transfer = self.__loadTransaction(testee, 'transaction-tx')

        # act
        actual = [*testee._CoinbaseApiReader__processTransfer(transfer, 2024)]

        # assert
        assert len(actual) == 0


    def test_processTransfer_StatusNotComplete_Skip(self, testee: CoinbaseApiReader):
        # arrange
        transfer = self.__loadTransaction(testee, 'transaction-tx')
        transfer['status'] = 'INVALID'

        # act
        actual = [*testee._CoinbaseApiReader__processTransfer(transfer, 2023)]

        # assert
        assert len(actual) == 0


    def test_processTransfer_UnknownType_Error(self, testee: CoinbaseApiReader):
        # arrange
        transfer = self.__loadTransaction(testee, 'transaction-tx')
        transfer['type'] = 'INVALID'

        # act and assert
        with raises(KeyError):
            [*testee._CoinbaseApiReader__processTransfer(transfer, 2023)]


    @mark.parametrize("fileName, year, type", [
        ('transaction-send',               2024, WithdrawTransfer),
        ('transaction-interest',           2024, Interest),
        ('transaction-staking_reward',     2024, Interest),
        ('transaction-staking_transfer',   2024, StartStake),
        ('transaction-unstaking_transfer', 2024, EndStake),
        ('transaction-tx',                 2023, AirDrop),
    ])
    def test_processTransfer_2023PlusTransferType_YieldType(self, testee: CoinbaseApiReader, fileName:str, year:int, type:Transaction):
        # arrange
        transfer = self.__loadTransaction(testee, fileName)

        # act
        actual = [*testee._CoinbaseApiReader__processTransfer(transfer, year)][0]

        # assert
        assert actual
        assert isinstance(actual, type)


    def test_processWithdrawal_Send_WithdrawTransfer(self, testee: CoinbaseApiReader):
        # arrange
        transfer = self.__loadTransaction(testee, 'transaction-send')

        # act
        actual = [*testee._CoinbaseApiReader__processWithdrawal(transfer)][0]

        # assert
        assert actual
        assert isinstance(actual, WithdrawTransfer)
        assert actual.id == 'b1d50800-228c-5704-9677-a6019aca1282'
        assert actual.mergentId == '==='
        assert actual.dateTime.year == 2024
        assert actual.amount.unit == 'USDC'
        assert actual.amount.amount == Decimal('10')
        assert actual.amount.amountRaw == Decimal('-10')
        assert actual.fee.unit == 'USDC'
        assert actual.fee.amount == 0
        assert actual.fee.amountRaw == 0
        assert actual.address == 'GABFQIK63R2NETJM7T673EAMZN4RJLLGP3OFUEJU5SZVTGWUKULZJNL6'


    def test_processInterest_Interest_Interest(self, testee:CoinbaseApiReader):
        # arrange
        transfer = self.__loadTransaction(testee, 'transaction-interest')

        # act
        actual = [*testee._CoinbaseApiReader__processInterest(transfer)][0]

        # assert
        assert actual
        assert isinstance(actual, Interest)
        assert actual.id == '690d27c7-a6c3-5f9e-bba0-bb031c6e233b'
        assert actual.mergentId == '==='
        assert actual.dateTime.year == 2024
        assert actual.amount.unit == 'USDC'
        assert actual.amount.amount == Decimal('199.324084')
        assert actual.amount.amountRaw == Decimal('199.324084')


    def test_processInterest_StakingReward_Interest(self, testee:CoinbaseApiReader):
        # arrange
        transfer = self.__loadTransaction(testee, 'transaction-staking_reward')

        # act
        actual = [*testee._CoinbaseApiReader__processInterest(transfer)][0]

        # assert
        assert actual
        assert isinstance(actual, Interest)
        assert actual.id == '24c29ca8-af6a-5d4b-87ed-bac5a68cb178'
        assert actual.mergentId == '==='
        assert actual.dateTime.year == 2024
        assert actual.amount.unit == 'ADA'
        assert actual.amount.amount == Decimal('0.354330')
        assert actual.amount.amountRaw == Decimal('0.354330')


    def test_processStartStake_StakingTransfer_StartStake(self, testee:CoinbaseApiReader):
        # arrange
        transfer = self.__loadTransaction(testee, 'transaction-staking_transfer')

        # act
        actual = [*testee._CoinbaseApiReader__processStartStake(transfer)][0]

        # assert
        assert actual
        assert isinstance(actual, StartStake)
        assert actual.id == '008021e0-0ba6-5c2c-b4c7-0efc721f0b38'
        assert actual.mergentId == '==='
        assert actual.dateTime.year == 2024
        assert actual.stakeId == None
        assert actual.amount.unit == 'ADA'
        assert actual.amount.amount == Decimal('1411.490000')
        assert actual.amount.amountRaw == Decimal('-1411.490000')
        assert actual.fee.unit == 'ADA'
        assert actual.fee.amount == 0
        assert actual.fee.amountRaw == 0


    def test_processEndStake_UnstakingTransfer_EndStake(self, testee:CoinbaseApiReader):
        # arrange
        transfer = self.__loadTransaction(testee, 'transaction-unstaking_transfer')

        # act
        actual = [*testee._CoinbaseApiReader__processEndStake(transfer)][0]

        # assert
        assert actual
        assert isinstance(actual, EndStake)
        assert actual.id == '7aba20b6-c84b-5143-9c6c-72ec5ff47c78'
        assert actual.mergentId == '==='
        assert actual.dateTime.year == 2024
        assert actual.stakeId == None
        assert actual.amount.unit == 'ADA'
        assert actual.amount.amount == Decimal('1414.288637')
        assert actual.amount.amountRaw == Decimal('1414.288637')
        assert actual.fee.unit == 'ADA'
        assert actual.fee.amount == 0
        assert actual.fee.amountRaw == 0


    def test_processAirDrop_Tx_AirDrop(self, testee:CoinbaseApiReader):
        # arrange
        transfer = self.__loadTransaction(testee, 'transaction-tx')

        # act
        actual = [*testee._CoinbaseApiReader__processAirDrop(transfer)][0]

        # assert
        assert actual
        assert isinstance(actual, AirDrop)
        assert actual.id == '97fe890f-5a05-5251-a28b-da7957671af3'
        assert actual.mergentId == '==='
        assert actual.dateTime.year == 2023
        assert actual.amount.unit == 'FLR'
        assert actual.amount.amount == Decimal('757.59000000')
        assert actual.amount.amountRaw == Decimal('757.59000000')

    
    def __loadTransaction(self, testee: CoinbaseApiReader, fileName:str):
        fill = TestData.loadJson(__file__, fileName)
        return testee._CoinbaseApiReader__transformTransfers(fill)

    #endregion

    #region Fills

    def test_processFill_BeforeYear_Skip(self, testee: CoinbaseApiReader):
        # arrange
        fill = self.__loadFill(testee, 'fill-BUY')

        # act
        actual = [*testee._CoinbaseApiReader__processFill(fill, 2025)]

        # assert
        assert len(actual) == 0


    def test_processFill_UnknownSide_Error(self, testee: CoinbaseApiReader):
        # arrange
        fill = self.__loadFill(testee, 'fill-BUY')
        fill['side'] = 'INVALID'

        # act and assert
        with raises(KeyError):
            [*testee._CoinbaseApiReader__processFill(fill, 2024)]


    def test_processBuy_Buy_BuyTrade(self, testee: CoinbaseApiReader):
        # arrange
        fill = self.__loadFill(testee, 'fill-BUY')
        sell = Decimal('0.00014082') * Decimal('068247.15')

        # act
        actual = [*testee._CoinbaseApiReader__processBuy(fill)][0]

        # assert
        assert actual
        assert isinstance(actual, BuyTrade)
        assert actual.id == '01e9de75-8061-44c1-9f68-368d71fe23ca'
        assert actual.mergentId == '==='
        assert actual.dateTime.year == 2024
        assert actual.buy.unit == 'BTC'
        assert actual.buy.amount == Decimal('0.00014082')
        assert actual.buy.amountRaw == Decimal('0.00014082')
        assert actual.sell.unit == 'USDC'
        assert actual.sell.amount == sell
        assert actual.sell.amountRaw == sell
        assert actual.fee.unit == 'USDC'
        assert actual.fee.amount == Decimal('0.0720792274725')
        assert actual.fee.amountRaw == Decimal('0.0720792274725')


    def test_processSell_Sell_SellTrade(self, testee: CoinbaseApiReader):
        # arrange
        fill = self.__loadFill(testee, 'fill-SELL')
        fee = Decimal('52.605158808375')
        buy = Decimal('0.21443868') * Decimal('98126.25') - fee

        # act
        actual = [*testee._CoinbaseApiReader__processSell(fill)][0]

        # assert
        assert actual
        assert isinstance(actual, SellTrade)
        assert actual.id == 'd9ffa84f-115d-4ac8-8a12-e1aef6dc9481'
        assert actual.mergentId == '==='
        assert actual.dateTime.year == 2024
        assert actual.sell.unit == 'BTC'
        assert actual.sell.amount == Decimal('0.21443868')
        assert actual.sell.amountRaw == Decimal('0.21443868')
        assert actual.buy.unit == 'USDC'
        assert actual.buy.amount == buy
        assert actual.buy.amountRaw == buy
        assert actual.fee.unit == 'USDC'
        assert actual.fee.amount == fee
        assert actual.fee.amountRaw == fee


    def __loadFill(self, testee: CoinbaseApiReader, fileName:str):
        fill = TestData.loadJson(__file__, fileName)
        return testee._CoinbaseApiReader__transformFills(fill)
    
    #endregion
