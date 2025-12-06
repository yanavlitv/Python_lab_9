import sys
import logging
from functools import wraps
import requests


def logger(func=None, *, handle=sys.stdout):
    """
    Декоратор для логирования вызовов функций.

    Args:
        func: Декорируемая функция
        handle: Объект для логирования (sys.stdout, io.StringIO, logging.Logger)
    """
    if func is None:
        return lambda f: logger(f, handle=handle)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Логируем старт
        start_msg = f"START {func.__name__} with args: {args}, kwargs: {kwargs}"

        if isinstance(handle, logging.Logger):
            handle.info(start_msg)
        else:
            handle.write(f"[INFO] {start_msg}\n")

        try:
            # Вызываем функцию
            result = func(*args, **kwargs)

            # Логируем успех
            success_msg = f"RETURN {func.__name__} -> {result}"

            if isinstance(handle, logging.Logger):
                handle.info(success_msg)
            else:
                handle.write(f"[INFO] {success_msg}\n")

            return result

        except Exception as e:
            # Логируем ошибку
            error_msg = f"ERROR {func.__name__} -> {type(e).__name__}: {str(e)}"

            if isinstance(handle, logging.Logger):
                handle.error(error_msg)
            else:
                handle.write(f"[ERROR] {error_msg}\n")

            raise

    return wrapper


@logger
def get_currencies(currency_codes: list, url: str = "https://www.cbr-xml-daily.ru/daily_json.js") -> dict:
    """
    Получает курсы валют с API Центробанка России.

    Args:
        currency_codes (list): Список символьных кодов валют (например, ['USD', 'EUR']).
        url (str): URL API Центробанка.

    Returns:
        dict: Словарь, где ключи - символьные коды валют, а значения - их курсы.
              Если валюта не найдена, значение будет строкой с сообщением об ошибке.

    Raises:
        ConnectionError: Если API недоступен или произошла ошибка подключения
        ValueError: Если получен некорректный JSON
        KeyError: Если в JSON отсутствует ключ "Valute" или запрошенная валюта
        TypeError: Если курс валюты имеет неверный тип
    """
    # Ситуация 1: Ошибки запроса к API
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        # Специфическая ошибка подключения
        raise ConnectionError(f"API недоступен: {e}")
    except requests.exceptions.Timeout as e:
        # Таймаут соединения
        raise ConnectionError(f"Таймаут при подключении к API: {e}")
    except requests.exceptions.RequestException as e:
        # Все остальные ошибки requests
        raise ConnectionError(f"Ошибка при запросе к API: {e}")

    # Ситуация 2: Парсим JSON
    try:
        data = response.json()
    except ValueError as e:
        raise ValueError(f"Некорректный JSON: {e}")

    # Ситуация 3: Проверяем наличие ключа "Valute"
    if "Valute" not in data:
        # ТЗ требует KeyError при отсутствии ключа "Valute"
        raise KeyError('Ключ "Valute" отсутствует в данных API')

    currencies = {}

    # Ситуация 4: Обрабатываем каждую запрошенную валюту
    for code in currency_codes:
        if code not in data["Valute"]:
            # ТЗ требует KeyError при отсутствии валюты
            raise KeyError(f"Валюта '{code}' отсутствует в данных")

        currency_data = data["Valute"][code]

        currency_id = currency_data.get("ID")
        num_code = currency_data.get("NumCode", "")
        char_code = currency_data.get("CharCode")
        nominal = currency_data.get("Nominal")
        name = currency_data.get("Name")
        value = currency_data.get("Value")

        # Проверяем тип курса валюты
        if not type(value) is float:
            raise TypeError(f"Курс валюты '{code}' имеет неверный тип: {type(value)}")

        currencies[code] = {'id': currency_id, 'num_code': num_code, 'char_code': char_code, 'nominal': nominal, 'name': name, 'value': value}

    return currencies