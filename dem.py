import logging
import sys
from homework import check_response, parse_status, check_tokens
# from tests.test_bot import test_check_response_no_homework


logger = logging.getLogger(__name__)
# Устанавливаем уровень, с которого логи будут сохраняться в файл
logger.setLevel(logging.INFO)
# Указываем обработчик логов
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

check_tokens()
# print(check_tokens())
if check_tokens():
    print(check_tokens())
else:
    print('NOT TRUE ', check_tokens())


# send_mes()
response = {
    'homeworks': [{'homework_name': 'hw5',
                   'status': 'reviewing'},
                  {'homework_name': 'hw4',
                  'status': 'rejected'}],
    'main': '144',
}
respon_1={}
response={}
# response = [1, 2, 3]


try:
    homeworks = check_response(response)
    homework = homeworks[0]
except Exception as error:
    logger.error(error)
else:
    print(parse_status(homework))
    print('Прога работает дальше')

    # homeworks = check_response(response)
    # homework = homeworks[0]
# print(homework)
# print(type(homework))
# test_check_response_no_homework()
# print(parse_status(homework))
    # print(parse_status(homework))
    # print('Прога работает дальше')

# print(not isinstance(response, dict))
# print(response == respon_1)
#     print('1')
# else:
#     print('2')
