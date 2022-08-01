class ErrorSend(Exception):
    """Базовый класс для исключений, которые необходимо отправить."""

    pass


class NoSendMessage(ErrorSend):
    """Сообщение не отправлено."""

    pass


class NoGetApiAnswer(ErrorSend):
    """Ошибка в запросе к эндпоинту API-сервиса."""

    pass


class ResponseTypeError(TypeError):
    """Ошибка в ответе от API-сервиса: тип данных не словарь."""

    pass


class ResponseKeyError(ErrorSend):
    """
    Ошибка в ответе от API-сервиса: отсутствует ключ "homeworks" или
    'current_date'.
    """

    pass


class HomeworksTypeError(ErrorSend):
    """Ошибка в ответе от API-сервиса: тип данных "homeworks" не список."""

    pass


class StatusKeyError(KeyError):
    """Ошибка в получении статуса домашней работы."""

    pass
