from controllers.databasecontroller import DatabaseController


class UserController:
    def __init__(self, db_controller: DatabaseController):
        self.db = db_controller

    def list_users(self):
        """Получить список всех пользователей"""
        users = self.db.read_users()

        # Добавляем информацию о подписках
        for user in users:
            user['subscriptions'] = self.db.get_user_subscriptions(user['id'])
            user['subscriptions_count'] = len(user['subscriptions'])

        return users

    def get_user(self, user_id: int):
        """Получить пользователя по ID с подписками"""
        user = self.db.read_user_by_id(user_id)
        if user:
            user['subscriptions'] = self.db.get_user_subscriptions(user_id)
        return user

    def add_subscription(self, user_id: int, currency_id: int):
        """Добавить подписку пользователя на валюту"""
        return self.db.add_user_subscription(user_id, currency_id)

    def remove_subscription(self, user_id: int, currency_id: int):
        """Удалить подписку пользователя"""
        return self.db.remove_user_subscription(user_id, currency_id)