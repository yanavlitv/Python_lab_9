import unittest
from models.currency import Currency


class TestCurrencyModel(unittest.TestCase):
    def test_currency_creation(self):
        currency = Currency(
            num_code="840",
            char_code="USD",
            name="Доллар США",
            value=90.0,
            nominal=1
        )
        self.assertEqual(currency.char_code, "USD")
        self.assertEqual(currency.name, "Доллар США")
        self.assertEqual(currency.value, 90.0)

    def test_currency_char_code_setter(self):
        currency = Currency(
            num_code="840",
            char_code="usd",
            name="Доллар США",
            value=90.0,
            nominal=1
        )
        currency.char_code = "EUR"
        self.assertEqual(currency.char_code, "EUR")

    def test_currency_char_code_validation(self):
        currency = Currency(
            num_code="840",
            char_code="USD",
            name="Доллар США",
            value=90.0,
            nominal=1
        )
        with self.assertRaises(ValueError):
            currency.char_code = "US"  # Должно быть 3 символа