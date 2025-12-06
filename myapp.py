from urllib.parse import urlparse, parse_qs
from jinja2 import Environment, PackageLoader, select_autoescape
from http.server import HTTPServer, BaseHTTPRequestHandler
from models import Author, User, Currency, App
from controllers import DatabaseController, CurrencyController, UserController
from utils.currencies_api import get_currencies
from utils.char_codes import get_char_codes
import json

# Jinja2 окружение
env = Environment(
    loader=PackageLoader("myapp"),
    autoescape=select_autoescape()
)

# Инициализация контроллеров БД
db_controller = DatabaseController()
currency_controller = CurrencyController(db_controller)
user_controller = UserController(db_controller)

# Загрузка шаблонов
template_index = env.get_template("index.html")
template_users = env.get_template("users.html")
template_currencies = env.get_template("currencies.html")
template_author = env.get_template("author.html")

main_author = Author("Яна Литвиновская", "Р3124")
app_instance = App("Вывод валют", "1.0", main_author)


def initialize_currencies():
    """Инициализация валют из API"""
    try:
        # Получаем список кодов валют
        currency_codes = get_char_codes()

        # Берем первые 20 валют для примера
        selected_codes = currency_codes[:20]

        # Получаем курсы валют
        currency_values = get_currencies(selected_codes)

        # Сохраняем валюты в БД
        for code, data in currency_values.items():
            currency_data = {
                'num_code': data.get('num_code', ''),
                'char_code': code,
                'name': data.get('name', ''),
                'value': float(data.get('value', 0)),
                'nominal': int(data.get('nominal', 1))
            }

            # Проверяем, существует ли валюта
            existing_currencies = currency_controller.list_currencies()
            exists = any(c['char_code'] == code for c in existing_currencies)

            if not exists:
                try:
                    currency_controller.create_currency(currency_data)
                except Exception as e:
                    print(f"Ошибка при создании валюты {code}: {e}")

        # Добавляем подписки для пользователей
        users = user_controller.list_users()
        currencies = currency_controller.list_currencies()

        # Находим популярные валюты
        popular_codes = ['USD', 'EUR', 'GBP', 'CNY', 'JPY']
        currency_ids = {}

        for currency in currencies:
            if currency['char_code'] in popular_codes:
                currency_ids[currency['char_code']] = currency['id']

        # Добавляем подписки для каждого пользователя
        for user in users[:3]:  # Для первых 3 пользователей
            for code in ['USD', 'EUR']:  # Подписываем на USD и EUR
                if code in currency_ids:
                    try:
                        user_controller.add_subscription(user['id'], currency_ids[code])
                    except Exception as e:
                        print(f"Ошибка при добавлении подписки: {e}")

    except Exception as e:
        print(f"Ошибка при инициализации валют: {e}")


# Инициализируем валюты
initialize_currencies()


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Парсим URL с помощью urlparse
        parsed_url = urlparse(self.path)
        path = parsed_url.path  # Чистый путь без параметров
        params = parse_qs(parsed_url.query)  # Параметры запроса

        # Маршрутизация на основе распарсенного пути
        if path == '/' or path == '/index':
            self.show_index(params)
        elif path == '/users':
            self.show_users(params)
        elif path == '/author':
            self.show_author(params)
        elif path == '/user':
            self.show_user(params)
        elif path == '/currencies':
            self.show_currencies(params)
        elif path == '/currency/add':
            self.add_currency(params)
        elif path == '/currency/delete':
            self.delete_currency(params)
        elif path == '/currency/update':
            self.update_currency(params)
        elif path == '/currency/show':
            self.show_currencies_console(params)
        else:
            self.send_error(404, "Страница не найдена")

    def show_index(self, params=None):
        """Главная страница"""
        # Получаем данные из БД
        currencies = currency_controller.list_currencies()
        users = user_controller.list_users()

        # Считаем общее количество подписок
        total_subscriptions = 0
        for user in users:
            total_subscriptions += len(user.get('subscriptions', []))

        result = template_index.render(
            myapp=app_instance.name,
            author_name=main_author.name,
            author_group=main_author.group,
            stats={
                'users_count': len(users),
                'currencies_count': len(currencies),
                'subscriptions_count': total_subscriptions
            }
        )

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(result.encode("utf-8"))

    def show_author(self, params=None):
        """Страница об авторе"""
        result = template_author.render(
            myapp=app_instance.name,
            author_name=main_author.name,
            author_group=main_author.group
        )

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(result.encode("utf-8"))

    def show_users(self, params=None):
        """Список пользователей"""
        user_id_str = params.get('user_id', [''])[0] if params else ''
        selected_user = None

        if user_id_str and user_id_str.isdigit():
            selected_user = user_controller.get_user(int(user_id_str))

        # Получаем всех пользователей
        users = user_controller.list_users()

        result = template_users.render(
            myapp=app_instance.name,
            users=users,
            selected_user=selected_user,
            user_subscriptions=selected_user.get('subscriptions', []) if selected_user else []
        )

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(result.encode("utf-8"))

    def show_user(self, params=None):
        """Информация о пользователе (/user?id=...)"""
        user_id = params.get('id', [''])[0] if params else ''

        if user_id:
            # Перенаправляем на /users?user_id=...
            self.send_response(302)
            self.send_header('Location', f'/users?user_id={user_id}')
            self.end_headers()
        else:
            self.send_error(400, "Не указан ID пользователя")

    def show_currencies(self, params=None):
        """Список валют с поиском"""
        search = params.get('search', [''])[0] if params else ''

        # Получаем валюты из БД с поиском
        currencies_data = currency_controller.list_currencies(search)

        # Подготавливаем данные для шаблона
        currencies_list = []
        for currency in currencies_data:
            # Получаем количество пользователей, подписанных на валюту
            users_count = db_controller.get_currency_users_count(currency['id'])

            # Создаем объект Currency для шаблона
            currency_obj = Currency(
                id=currency['id'],
                num_code=currency['num_code'],
                char_code=currency['char_code'],
                name=currency['name'],
                value=currency['value'],
                nominal=currency['nominal']
            )

            currencies_list.append({
                'currency': currency_obj,
                'users_count': users_count
            })

        result = template_currencies.render(
            myapp=app_instance.name,
            currencies=currencies_list,
            total=len(currencies_data),
            search_query=search
        )

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(result.encode("utf-8"))

    def add_currency(self, params=None):
        """Добавление новой валюты по символьному коду"""
        if params:
            # Получаем символьный код из формы
            char_code = params.get('char_code', [''])[0].strip().upper()

            # Проверяем обязательное поле
            if not char_code:
                self.send_error(400, "Укажите символьный код валюты (например: USD, EUR)")
                return

            # Проверяем формат кода 
            if len(char_code) != 3 or not char_code.isalpha():
                self.send_error(400, "Символьный код должен состоять из 3 латинских букв")
                return

            try:
                # Проверяем, не существует ли уже валюта с таким кодом
                existing_currencies = currency_controller.list_currencies()
                exists = any(c['char_code'] == char_code for c in existing_currencies)

                if exists:
                    self.send_error(400, f"Валюта с кодом {char_code} уже существует в базе")
                    return

                # Получаем данные о валюте из API
                try:
                    # Используем функцию get_currencies для получения данных по одной валюте
                    currency_data_from_api = get_currencies([char_code])

                    if char_code not in currency_data_from_api:
                        self.send_error(400, f"Валюта с кодом {char_code} не найдена в API ЦБ РФ")
                        return

                    # Извлекаем данные из API ответа
                    api_data = currency_data_from_api[char_code]

                    currency_data = {
                        'num_code': api_data.get('num_code', ''),
                        'char_code': char_code,
                        'name': api_data.get('name', ''),
                        'value': float(api_data.get('value', 0)),
                        'nominal': int(api_data.get('nominal', 1))
                    }

                except Exception as api_error:
                    self.send_error(500, f"Ошибка при получении данных из API: {api_error}")
                    return

                # Добавляем валюту в БД
                new_currency_id = currency_controller.create_currency(currency_data)

                if new_currency_id:
                    print(f"Добавлена новая валюта: {char_code} ({currency_data['name']})")
                    print(f"  Курс: {currency_data['value']} руб. за {currency_data['nominal']} ед.")
                    # Перенаправляем на страницу валют
                    self.send_response(302)
                    self.send_header('Location', '/currencies')
                    self.end_headers()
                else:
                    self.send_error(500, "Ошибка при добавлении валюты в базу данных")

            except ValueError as e:
                self.send_error(400, f"Некорректные данные: {e}")
            except Exception as e:
                self.send_error(500, f"Ошибка сервера: {e}")
        else:
            self.send_error(400, "Не указан символьный код валюты")

    def delete_currency(self, params=None):
        """Удаление валюты по ID"""
        currency_id = params.get('id', [''])[0] if params else ''

        if currency_id and currency_id.isdigit():
            currency_id_int = int(currency_id)

            # Проверяем, существует ли валюта
            currency = db_controller.read_currency_by_id(currency_id_int)

            if currency:
                # Удаляем валюту
                if currency_controller.delete_currency(currency_id_int):
                    # Перенаправляем на страницу валют
                    self.send_response(302)
                    self.send_header('Location', '/currencies')
                    self.end_headers()
                else:
                    self.send_error(500, "Ошибка при удалении валюты")
            else:
                self.send_error(404, "Валюта не найдена")
        else:
            self.send_error(400, "Не указан корректный ID валюты")

    def update_currency(self, params=None):
        """Обновление курса валюты"""
        updated = False

        if params:
            # Ищем параметры с кодами валют (USD, EUR и т.д.)
            for param_name, param_value in params.items():
                # Проверяем, что параметр похож на код валюты (3 буквы)
                if len(param_name) == 3 and param_name.isalpha():
                    currency_code = param_name.upper()

                    if param_value and param_value[0]:
                        try:
                            new_value = float(param_value[0])

                            # Находим валюту по коду
                            currencies = currency_controller.list_currencies()
                            target_currency = None

                            for currency in currencies:
                                if currency['char_code'] == currency_code:
                                    target_currency = currency
                                    break

                            if target_currency:
                                # Обновляем курс
                                if currency_controller.update_currency_value(target_currency['id'], new_value):
                                    updated = True
                                    print(f"Курс {currency_code} обновлен до {new_value}")

                        except ValueError:
                            print(f"Некорректное значение для {currency_code}: {param_value[0]}")

        if updated:
            # Перенаправляем на страницу валют
            self.send_response(302)
            self.send_header('Location', '/currencies')
            self.end_headers()
        else:
            # Если ничего не обновили, показываем ошибку
            self.send_error(400, "Не удалось обновить курсы. Проверьте данные.")

    def show_currencies_console(self, params=None):
        """Вывод валют в консоль (для отладки)"""
        # Получаем параметр поиска если есть
        search = params.get('search', [''])[0] if params else ''

        currencies = currency_controller.list_currencies(search)

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()

        result = "=" * 60 + "\n"
        result += "СПИСОК ВАЛЮТ ИЗ БАЗЫ ДАННЫХ\n"
        if search:
            result += f"Поиск: '{search}'\n"
        result += "=" * 60 + "\n\n"

        for currency in currencies:
            users_count = db_controller.get_currency_users_count(currency['id'])
            result += f"{currency['char_code']} - {currency['name']}\n"
            result += f"  ID: {currency['id']}\n"
            result += f"  Курс: {currency['value']} руб. за {currency['nominal']} ед.\n"
            result += f"  Подписчиков: {users_count}\n"
            result += "-" * 40 + "\n"

        result += f"\nВсего валют: {len(currencies)}\n"

        self.wfile.write(result.encode("utf-8"))

    def send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()

        error_text = f"Ошибка {code}: {message}\nПерейдите на /"
        self.wfile.write(error_text.encode("utf-8"))


if __name__ == '__main__':
    httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
    print('=' * 50)
    print('Сервер запущен: http://localhost:8080')
    httpd.serve_forever()
