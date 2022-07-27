import logging
import os
import sys
import time

from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DICT_TOKKEN = {'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
               'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
               'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
               }

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logger.error(f'Сообщение не отправлено'
                     f'\nОшибка: {error}')
    else:
        logger.info('Сообщение отправлено')
        pass


def get_api_answer(current_timestamp):
    """Запрос к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != HTTPStatus.OK:
        message_err: str = response.json()['message']
        logger.error(message_err)
    return response.json()


def check_response(response):
    """Проверка полученных данных."""
    key = list(response)
    if not isinstance(response, dict):
        logger.error(' Response data type is not correct.'
                     '\n Тип данных ответа неверен')
        raise TypeError('Response data type is not correct.')
    elif 'homeworks' not in key:
        logger.error('No key "homeworks"'
                     '\n При ответе отсутствует ключ "homeworks".')
        raise KeyError('При ответе отсутствует ключ "homeworks".')
    elif type(response.get('homeworks')) is not list:
        logger.error('"homeworks" type is not list')
        raise TypeError('"homeworks" type is not list.')
    else:
        return response.get('homeworks')


def parse_status(homework):
    """Получение данных о домашней работе."""
    global verdict
    homework_name = homework.get('homework_name')
    status_key = list(HOMEWORK_STATUSES)
    homework_status = homework.get('status')
    if homework_status not in status_key:
        logger.info('Значение status некорректно')
        raise KeyError('Значение status некорректно')
    else:
        for key in HOMEWORK_STATUSES:
            if homework_status == key:
                verdict = HOMEWORK_STATUSES[key]
                break
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка данных токенов."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID is not None:
        return True
    else:
        logger.critical('Отсутствуют обязательные переменные окружения')
        return False


def main():
    """Основная логика работы бота."""
    previous_homeworks = {}
    homeworks_null = []
    previous_error = ''
    current_timestamp = 1654842489
    bot = Bot(token=TELEGRAM_TOKEN)
    while True:
        try:
            check_tokens()
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks == homeworks_null:
                current_homework = dict(homeworks)
            else:
                current_homework = homeworks[0]
            if previous_homeworks == current_homework:
                logger.debug('Отсутствуют новые статусы')
                pass
            else:
                previous_homeworks = dict(current_homework)
                text = parse_status(current_homework)
                send_message(bot, text)

            current_timestamp = int(response.get('current_date'))

            time.sleep(RETRY_TIME)

        except Exception as error:
            new_error = error
            if str(previous_error) != str(new_error):
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
                previous_error = error
            else:
                pass
            time.sleep(RETRY_TIME)
        else:
            logger.info('При работе программы ошибок нет.')


if __name__ == '__main__':
    main()
