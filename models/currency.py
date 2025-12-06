class Currency:
    def __init__(self, id: int = None, num_code: str = None, char_code: str = None,
                 name: str = None, value: float = None, nominal: int = None):
        self.__id = id
        self.__num_code = num_code
        self.__char_code = char_code
        self.__name = name
        self.__value = value
        self.__nominal = nominal

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
    def num_code(self):
        return self.__num_code

    @num_code.setter
    def num_code(self, num_code: str):
        if type(num_code) is str and len(num_code.strip()) > 0:
            self.__num_code = num_code.strip()
        else:
            raise ValueError('Цифровой код должен быть непустой строкой')

    @property
    def char_code(self):
        return self.__char_code

    @char_code.setter
    def char_code(self, char_code: str):
        char_code = char_code.strip()
        if type(char_code) is str and len(char_code) == 3 and char_code.isalpha():
            self.__char_code = char_code.upper()
        else:
            raise ValueError('Символьный код должен состоять из 3 букв')

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name: str):
        name = name.strip()
        if type(name) is str and len(name) >= 2:
            self.__name = name
        else:
            raise ValueError('Название валюты должно быть строкой длиной не менее 2 символов')

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: float):
        if value is None or (type(value) in (int, float) and value >= 0):
            self.__value = float(value) if value is not None else None
        else:
            raise ValueError('Курс валюты должен быть неотрицательным числом')

    @property
    def nominal(self):
        return self.__nominal

    @nominal.setter
    def nominal(self, nominal: int):
        if nominal is None or (type(nominal) is int and nominal > 0):
            self.__nominal = nominal
        else:
            raise ValueError('Номинал должен быть положительным целым числом')

    def __str__(self):
        if self.__value and self.__nominal:
            return f"{self.__char_code} - {self.__name} ({self.__value} руб. за {self.__nominal} ед.)"
        return f"{self.__char_code} - {self.__name}"

    def __repr__(self):
        return (f"Currency(id={self.__id!r}, num_code={self.__num_code!r}, "
                f"char_code={self.__char_code!r}, name={self.__name!r}, "
                f"value={self.__value}, nominal={self.__nominal})")