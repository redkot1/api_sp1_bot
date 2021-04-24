import os
import time

import requests
import telegram
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, filename='logs.log', filemode='w')
logger = logging.getLogger(__name__)

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRAKTIKUM_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать'\
            ' к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    if current_timestamp is None:
        current_timestamp = int(time.time())
    try:
        logger.info('Запрос на сервер отправлен')
        homework_statuses = requests.get(
            PRAKTIKUM_URL,
            params={'from_date': current_timestamp},
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}', }
        )
        logger.info('Ответ с сервера получен', homework_statuses.json())
        return homework_statuses.json()
    except Exception as error:
        error_text = f'Бот столкнулся с ошибкой: {error}'
        bot_client.send_message(chat_id=CHAT_ID, text=error_text)
        logger.error(
            f'Бот столкнулся с ошибкой: {error}',
            exc_info=True
        )
        time.sleep(5)


def send_message(message, bot_client):
    logger.debug(f'Сообщение: {message} отправлено!')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.debug('Бот инициализизован')
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]),
                    bot_client)
                logger.info('Сообщение отправлено')
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp)
            logger.info('timestamp обновлен')
            time.sleep(300)

        except Exception as e:
            logger.error(e, exc_info=True)
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
