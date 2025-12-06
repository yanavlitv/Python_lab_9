from models.user import User
from models.currency import Currency

class UserCurrency:
    def __init__(self, id: int = None, user_id: int = None, currency_id: int = None,
                 user: User = None, currency: Currency = None):
        self.__id = id
        self.__user_id = user_id
        self.__currency_id = currency_id
        self.__user = user
        self.__currency = currency

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id: int):
        if id is None or (type(id) is int and id > 0):
            self.__id = id
        else:
            raise ValueError('ID должен быть положительным целым числом')

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, user_id: int):
        if user_id is None or (type(user_id) is int and user_id > 0):
            self.__user_id = user_id
        else:
            raise ValueError('user_id должен быть положительным целым числом')

    @property
    def currency_id(self):
        return self.__currency_id

    @currency_id.setter
    def currency_id(self, currency_id: int):
        if currency_id is None or (type(currency_id) is int and currency_id > 0):
            self.__currency_id = currency_id
        else:
            raise ValueError('currency_id должен быть положительным целым числом')

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, user: User):
        if user is None or isinstance(user, User):
            self.__user = user
            if user is not None:
                self.__user_id = user.id
        else:
            raise ValueError('user должен быть объектом типа User или None')

    @property
    def currency(self):
        return self.__currency

    @currency.setter
    def currency(self, currency: Currency):
        if currency is None or isinstance(currency, Currency):
            self.__currency = currency
            if currency is not None:
                self.__currency_id = currency.id
        else:
            raise ValueError('currency должен быть объектом типа Currency или None')

    def __str__(self):
        user_info = self.__user.name if self.__user else f"id={self.__user_id}"
        currency_info = self.__currency.char_code if self.__currency else f"id={self.__currency_id}"
        return f"UserCurrency(id={self.__id}, user={user_info}, currency={currency_info})"

    def __repr__(self):
        return self.__str__()