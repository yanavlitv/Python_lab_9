import requests

def get_char_codes(url: str = "https://www.cbr-xml-daily.ru/daily_json.js") -> list:
    """
    Получает список символьных кодов валют с API Центробанка.

    Args:
        url (str): URL API Центробанка

    Returns:
        List[str]: Отсортированный список символьных кодов валют

    Raises:
        ConnectionError: Если не удалось подключиться к API
        ValueError: Если получен некорректный JSON
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
    char_codes = []
    for currency_data in data["Valute"].values():
        char_code = currency_data.get("CharCode")
        char_codes.append(char_code)

    # Сортируем и возвращаем уникальные значения
    return char_codes

