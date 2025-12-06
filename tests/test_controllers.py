import unittest
from unittest.mock import MagicMock
from controllers.currencycontroller import CurrencyController

class TestCurrencyController(unittest.TestCase):
    def test_list_currencies(self):
        mock_db = MagicMock()
        mock_db.read_currencies.return_value = [
            {"id": 1, "char_code": "USD", "value": 90.0}
        ]
        controller = CurrencyController(mock_db)
        result = controller.list_currencies()
        self.assertEqual(result[0]['char_code'], "USD")
        mock_db.read_currencies.assert_called_once()

    def test_delete_currency(self):
        mock_db = MagicMock()
        mock_db.delete_currency.return_value = True
        controller = CurrencyController(mock_db)
        result = controller.delete_currency(1)
        self.assertTrue(result)
        mock_db.delete_currency.assert_called_once_with(1)