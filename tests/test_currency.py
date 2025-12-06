import unittest
from unittest.mock import MagicMock
from controllers.currencycontroller import CurrencyController
from controllers.databasecontroller import DatabaseController


class TestCurrencyController(unittest.TestCase):
    def test_list_currencies(self):
        mock_db = MagicMock(spec=DatabaseController)
        mock_db.read_currencies.return_value = [
            {"id": 1, "char_code": "USD", "value": 90.0, "name": "Доллар США"}
        ]

        controller = CurrencyController(mock_db)
        result = controller.list_currencies()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['char_code'], "USD")
        mock_db.read_currencies.assert_called_once()

    def test_update_currency_value_negative(self):
        mock_db = MagicMock(spec=DatabaseController)
        controller = CurrencyController(mock_db)

        with self.assertRaises(ValueError):
            controller.update_currency_value(1, -10.0)


if __name__ == '__main__':
    unittest.main()