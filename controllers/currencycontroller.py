from controllers.databasecontroller import DatabaseController
from models.currency import Currency


class CurrencyController:
    def __init__(self, db_controller: DatabaseController):
        self.db = db_controller

    def list_currencies(self, search: str = None):
        """Получить список всех валют"""
        return self.db.read_currencies(search)

    def get_currency(self, currency_id: int):
        """Получить валюту по ID"""
        return self.db.read_currency_by_id(currency_id)

    def create_currency(self, currency_data: dict):
        """Создать новую валюту"""
        # Проверяем обязательные поля
        required_fields = ['num_code', 'char_code', 'name', 'value', 'nominal']
        for field in required_fields:
            if field not in currency_data:
                raise ValueError(f"Отсутствует обязательное поле: {field}")

        # Создаем объект Currency для валидации
        currency = Currency(
            num_code=currency_data['num_code'],
            char_code=currency_data['char_code'],
            name=currency_data['name'],
            value=currency_data['value'],
            nominal=currency_data['nominal']
        )

        # Сохраняем в БД
        return self.db.create_currency(currency_data)

    def update_currency_value(self, currency_id: int, value: float):
        """Обновить курс валюты"""
        if value < 0:
            raise ValueError("Курс валюты не может быть отрицательным")

        return self.db.update_currency(currency_id, value)

    def delete_currency(self, currency_id: int):
        """Удалить валюту"""
        return self.db.delete_currency(currency_id)