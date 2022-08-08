import enum
import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot, TelegramError

from exceptions import (HomeworksTypeError, NoGetApiAnswer, NoSendMessage,
                        ResponseKeyError, ResponseTypeError, StatusKeyError)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)


class TextSettings(enum.Enum):
    """Класс для настройки текстовых сообщений."""

    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except TelegramError:
        raise NoSendMessage('Сообщение не отправлено.')
    else:
        logger.info('Сообщение отправлено')


def get_api_answer(current_timestamp):
    """Запрос к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != HTTPStatus.OK:
        raise NoGetApiAnswer('Ошибка в запросе к эндпоинту API-сервиса.')
    return response.json()


def check_response(response):
    """Проверка полученных данных."""
    if not isinstance(response, dict):
        raise ResponseTypeError(
            "Ошибка в ответе от API-сервиса: тип данных не словарь.")
    elif not response.keys() >= {'homeworks', 'current_date'}:
        raise ResponseKeyError(
            'Ошибка в ответе от API - сервиса: отсутствует ключ "homeworks" '
            'или "current_date".')
    elif not isinstance(response.get('homeworks'), list):
        raise HomeworksTypeError(
            'Ошибка в ответе от API-сервиса: тип данных "homeworks" '
            'не список.')
    return response.get('homeworks')


def parse_status(homework):
    """Получение данных о домашней работе."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if not homework_name:
        raise StatusKeyError('Ошибка: нет ключа "homework_name" в ответе. '
                             'Возможно изменения в API')
    elif homework_status not in HOMEWORK_STATUSES:
        raise StatusKeyError('Ошибка: пришел незадокументированный статус.'
                             'Возможно изменения в API')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка данных токенов."""
    return all(
        [PRACTICUM_TOKEN,
         TELEGRAM_TOKEN,
         TELEGRAM_CHAT_ID]
    )


def main():
    """Основная логика работы бота."""
    previous_homeworks = {}
    new_error = ''
    previous_error = ''
    current_timestamp = int(time.time())
    if not check_tokens():
        if TELEGRAM_CHAT_ID and TELEGRAM_TOKEN:
            bot = Bot(token=TELEGRAM_TOKEN)
            message = ('Проблема с токеном для Практикум.Яндекс. '
                       'Программа остановлена')
            send_message(bot, message)
        else:
            message = ('Проблема с токеном для Telegram. '
                       'Программа остановлена')
        sys.exit(logger.critical(
            TextSettings.RED.value + message + TextSettings.END.value))
    bot = Bot(token=TELEGRAM_TOKEN)
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                current_homework = homeworks[0]
                text = parse_status(current_homework)
            else:
                current_homework = dict(homeworks)
                text = 'Homework: нулевой список'
            if previous_homeworks == current_homework:
                logger.debug('Отсутствуют новые статусы')
            else:
                previous_homeworks = dict(current_homework)
                send_message(bot, text)
            current_timestamp = int(response.get('current_date'))
        except StatusKeyError as error:
            logger.info(error)
        except Exception as error:
            new_error = error
            logger.error(
                TextSettings.RED.value + str(error) + TextSettings.END.value)
        else:
            logger.info('При работе программы ошибок нет.')
        finally:
            if new_error:
                if str(previous_error) != str(new_error):
                    message = f'Сбой в работе программы: {new_error}'
                    send_message(bot, message)
                    previous_error = new_error
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
