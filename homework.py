import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot

from exceptions import (HomeworksTypeError, NoGetApiAnswer, NoSendMessage,
                        ResponseKeyError, ResponseTypeError,
                        StatusKeyError)

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


class text_settings:
    """Класс для настройки текстовых сообщений."""

    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def def_text_error(raisename):
    """Функция для сообщений: Error."""
    text_error = raisename.__doc__
    logger.error(text_settings.RED + text_error + text_settings.END)
    new_error = text_error
    return new_error


def def_text_info(raisename):
    """Функция для сообщений: Info."""
    text_info = raisename.__doc__
    logger.info(text_info)


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except:
        raise NoSendMessage
    logger.info('Сообщение отправлено')


def get_api_answer(current_timestamp):
    """Запрос к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != HTTPStatus.OK:
        raise NoGetApiAnswer
    return response.json()


def check_response(response):
    """Проверка полученных данных."""
    if not isinstance(response, dict):
        raise ResponseTypeError
    elif not response.keys() >= {'homeworks', 'current_date'}:
        raise ResponseKeyError
    elif not isinstance(response.get('homeworks'), list):
        raise HomeworksTypeError
    return response.get('homeworks')


def parse_status(homework):
    """Получение данных о домашней работе."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status in HOMEWORK_STATUSES:
        for key in HOMEWORK_STATUSES:
            if homework_status == key:
                verdict = HOMEWORK_STATUSES[key]
                break
    else:
        raise StatusKeyError
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
            text_settings.RED + message + text_settings.END))
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
        except NoSendMessage:
            new_error = def_text_error(NoSendMessage)
        except NoGetApiAnswer:
            new_error = def_text_error(NoGetApiAnswer)
        except ResponseTypeError:
            new_error = def_text_error(ResponseTypeError)
        except ResponseKeyError:
            new_error = def_text_error(ResponseKeyError)
        except HomeworksTypeError:
            new_error = def_text_error(HomeworksTypeError)
        except StatusKeyError:
            def_text_info(StatusKeyError)
        except Exception as error:
            new_error = error
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
