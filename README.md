#Цель работы

Реализовать CRUD (Create, Read, Update, Delete) для сущностей бизнес-логики приложения.

Освоить работу с SQLite в памяти (:memory:) через модуль sqlite3.

Понять принципы первичных и внешних ключей и их роль в связях между таблицами.

Выделить контроллеры для работы с БД и для рендеринга страниц в отдельные модули.

Использовать архитектуру MVC и соблюдать разделение ответственности.

Отображать пользователям таблицу с валютами, на которые они подписаны.

Реализовать полноценный роутер, который обрабатывает GET-запросы и выполняет сохранение/обновление данных и рендеринг страниц.

Научиться тестировать функционал на примере сущностей currency и user с использованием unittest.mock.

#Модели, свойства и связи

##Модель Currency (Валюта):

id - первичный ключ (INTEGER)

num_code - цифровой код (TEXT)

char_code - символьный код, 3 буквы (TEXT)

name - название валюты (TEXT)

value - курс к рублю (REAL)

nominal - номинал (INTEGER)

##Модель User (Пользователь):

id - первичный ключ

name - имя пользователя

##Модель UserCurrency (Связь):

id - первичный ключ

user_id - внешний ключ к User

currency_id - внешний ключ к Currency

Связи: User (1) ↔ (n) UserCurrency (n) ↔ (1) Currency

```python
├── myapp.py                    # Главный файл приложения
├── requirements.txt           # Зависимости
├── models/                    # Модели данных
│   ├── __init__.py
│   ├── author.py            # Автор приложения
│   ├── user.py              # Пользователь
│   ├── currency.py          # Валюта (основная модель)
│   ├── app.py              # Приложение
│   └── user_currency.py     # Связь пользователей и валют
├── controllers/              # Контроллеры
│   ├── __init__.py
│   ├── databasecontroller.py  # Работа с SQLite
│   ├── currencycontroller.py  # Управление валютами
│   └── usercontroller.py     # Управление пользователями
├── templates/                # HTML шаблоны (View)
│   ├── index.html           # Главная страница
│   ├── users.html           # Пользователи
│   ├── currencies.html      # Валюты
│   └── author.html          # Об авторе
└── utils/                   # Вспомогательные модули
    ├── __init__.py
    ├── currencies_api.py    # API ЦБ РФ
    └── char_codes.py        # Получение кодов валют
```
#Реализация CRUD с SQL-запросами
```python
#CREATE:
sql
INSERT INTO currency(num_code, char_code, name, value, nominal) 
VALUES(:num_code, :char_code, :name, :value, :nominal)
#READ:
sql
SELECT * FROM currency WHERE LOWER(name) LIKE ? OR LOWER(char_code) LIKE ?
#UPDATE:
sql
UPDATE currency SET value = ? WHERE id = ?
#DELETE:
sql
DELETE FROM currency WHERE id = ?
```
