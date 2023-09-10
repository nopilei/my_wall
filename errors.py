from typing import Optional


class TelegramError(Exception):
    default_message = 'Ошибка Telegram API'

    def __init__(self, error_message: Optional[str] = None):
        self.message = error_message if error_message is not None else self.default_message


class UnknownChannel(TelegramError):
    default_message = 'Данного канала не существует'


class InvalidLink(TelegramError):
    default_message = 'Ссылка невалидна'


class SubscribtionFailed(TelegramError):
    default_message = 'Не удалось подписаться на данный канал, попробуйте позже'


class UnsubscribableEntity(TelegramError):
    default_message = 'Нельзя подписаться на этот канал'


class AwaitingAcception(TelegramError):
    default_message = 'Запрос на подписку в обработке. Как только вашу заявку одобрят вы начнете получать сообщения'
