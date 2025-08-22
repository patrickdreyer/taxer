from taxer.transactions.transaction import Transaction


class TestTransaction:
    _MERGENT_ID = 'MERGENT_ID'
    _DATE_TIME = 'DATE_TIME'
    _ID = 'ID'
    _NOTE = 'NOTE'

    def test_ctor_argumentsSet(self):
        transaction = Transaction(TestTransaction._MERGENT_ID, TestTransaction._DATE_TIME, TestTransaction._ID, TestTransaction._NOTE)
        assert transaction.mergentId == TestTransaction._MERGENT_ID
        assert transaction.dateTime == TestTransaction._DATE_TIME
        assert transaction.id == TestTransaction._ID
        assert transaction.note == TestTransaction._NOTE
