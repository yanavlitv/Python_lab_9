class User:
    def __init__(self, id: int = None, name: str = None):
        self.__id = id
        self.__name = name

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id: int):
        if id is None or (type(id) is int and id > 0):
            self.__id = id
        else:
            raise ValueError('ID должен быть целым положительным числом')

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name: str):
        name = name.strip()
        if type(name) is str and len(name) >= 2:
            self.__name = name
        else:
            raise ValueError('Имя пользователя должно быть строкой длиной не менее 2 символов')

    def __str__(self):
        return f"User(id={self.__id}, name='{self.__name}')"

    def __repr__(self):
        return self.__str__()