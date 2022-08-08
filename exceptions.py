from telegram import TelegramError


class NoSendMessage(TelegramError):
    """Сообщение не отправлено."""

    pass


class NoGetApiAnswer(Exception):
    """Ошибка в запросе к эндпоинту API-сервиса."""

    pass


class ResponseTypeError(TypeError):
    """Ошибка в ответе от API-сервиса: тип данных не словарь."""

    pass


class ResponseKeyError(Exception):
    """
    Ошибка в ответе от API-сервиса: отсутствует ключ "homeworks" или
    'current_date'.
    """

    pass


class HomeworksTypeError(Exception):
    """Ошибка в ответе от API-сервиса: тип данных "homeworks" не список."""

    pass


class StatusKeyError(KeyError):
    """Ошибка в получении статуса домашней работы."""

    pass
