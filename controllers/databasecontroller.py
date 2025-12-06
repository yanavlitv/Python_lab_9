import sqlite3
from typing import List, Dict, Any


class DatabaseController:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._init_data()

    def _create_tables(self):
        # Создаем таблицу user
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')

        # Создаем таблицу currency
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS currency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                num_code TEXT NOT NULL,
                char_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                value REAL,
                nominal INTEGER
            )
        ''')

        # Создаем таблицу user_currency
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_currency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                currency_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(currency_id) REFERENCES currency(id),
                UNIQUE(user_id, currency_id)
            )
        ''')

        self.conn.commit()

    def _init_data(self):
        # Инициализируем тестовых пользователей
        users = [
            {"name": "Никита Свин"},
            {"name": "Артем Рыба"},
            {"name": "Матвей Груб"}
        ]

        sql = "INSERT INTO user(name) VALUES(:name)"
        self.cursor.executemany(sql, users)
        self.conn.commit()

    # CRUD для Currency
    def create_currency(self, currency_data: Dict[str, Any]) -> int:
        """Добавить новую валюту"""
        sql = '''INSERT INTO currency(num_code, char_code, name, value, nominal) 
                 VALUES(:num_code, :char_code, :name, :value, :nominal)'''
        self.cursor.execute(sql, currency_data)
        self.conn.commit()
        return self.cursor.lastrowid

    def read_currencies(self, search: str = None) -> List[Dict]:
        """Получить список валют с возможностью поиска"""
        if search:
            sql = '''SELECT * FROM currency 
                     WHERE LOWER(name) LIKE ? OR LOWER(char_code) LIKE ?'''
            self.cursor.execute(sql, (f'%{search.lower()}%', f'%{search.lower()}%'))
        else:
            sql = "SELECT * FROM currency"
            self.cursor.execute(sql)

        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def read_currency_by_id(self, currency_id: int) -> Dict:
        """Получить валюту по ID"""
        sql = "SELECT * FROM currency WHERE id = ?"
        self.cursor.execute(sql, (currency_id,))
        columns = [col[0] for col in self.cursor.description]
        row = self.cursor.fetchone()
        return dict(zip(columns, row)) if row else None

    def update_currency(self, currency_id: int, value: float) -> bool:
        """Обновить курс валюты"""
        sql = "UPDATE currency SET value = ? WHERE id = ?"
        self.cursor.execute(sql, (value, currency_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_currency(self, currency_id: int) -> bool:
        """Удалить валюту по ID"""
        # Сначала удаляем связи из user_currency
        sql1 = "DELETE FROM user_currency WHERE currency_id = ?"
        self.cursor.execute(sql1, (currency_id,))

        # Затем удаляем саму валюту
        sql2 = "DELETE FROM currency WHERE id = ?"
        self.cursor.execute(sql2, (currency_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # CRUD для User
    def read_users(self) -> List[Dict]:
        """Получить список пользователей"""
        sql = "SELECT * FROM user"
        self.cursor.execute(sql)
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def read_user_by_id(self, user_id: int) -> Dict:
        """Получить пользователя по ID"""
        sql = "SELECT * FROM user WHERE id = ?"
        self.cursor.execute(sql, (user_id,))
        columns = [col[0] for col in self.cursor.description]
        row = self.cursor.fetchone()
        return dict(zip(columns, row)) if row else None

    # Работа с подписками
    def get_user_subscriptions(self, user_id: int) -> List[Dict]:
        """Получить подписки пользователя"""
        sql = '''SELECT c.* FROM currency c
                 JOIN user_currency uc ON c.id = uc.currency_id
                 WHERE uc.user_id = ?'''
        self.cursor.execute(sql, (user_id,))
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def add_user_subscription(self, user_id: int, currency_id: int) -> bool:
        """Добавить подписку пользователя на валюту"""
        try:
            sql = "INSERT INTO user_currency(user_id, currency_id) VALUES(?, ?)"
            self.cursor.execute(sql, (user_id, currency_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Подписка уже существует
            return False

    def remove_user_subscription(self, user_id: int, currency_id: int) -> bool:
        """Удалить подписку пользователя"""
        sql = "DELETE FROM user_currency WHERE user_id = ? AND currency_id = ?"
        self.cursor.execute(sql, (user_id, currency_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_currency_users_count(self, currency_id: int) -> int:
        """Получить количество пользователей, подписанных на валюту"""
        sql = "SELECT COUNT(*) FROM user_currency WHERE currency_id = ?"
        self.cursor.execute(sql, (currency_id,))
        return self.cursor.fetchone()[0]

    def close(self):
        """Закрыть соединение с БД"""
        self.conn.close()

    def __del__(self):
        self.close()