####################################################################################################
LOGO = '''\
       _                _     _       _       __                _
__   _| | __  _ __ __ _(_) __| |   __| | ___ / _| ___ _ __   __| | ___ _ __
\ \ / / |/ / | '__/ _` | |/ _` |  / _` |/ _ \ |_ / _ \ '_ \ / _` |/ _ \ '__|
 \ V /|   <  | | | (_| | | (_| | | (_| |  __/  _|  __/ | | | (_| |  __/ |
  \_/ |_|\_\ |_|  \__,_|_|\__,_|  \__,_|\___|_|  \___|_| |_|\__,_|\___|_|

by alfred richardsn'''
####################################################################################################
import sys

try:
    from vk_api import VkApi
except ImportError:
    sys.exit('для работы vk-raid-defender необходима библиотека vk_api')

from vk_api.longpoll import VkLongPoll, VkEventType

import re
import os
import pickle
import logging
from time import time
from getpass import getpass


DATA_FILE_NAME = 'vk_raid_helper.dat'

try:
    with open(DATA_FILE_NAME, 'rb') as f:
        data = pickle.load(f)
except FileNotFoundError:
    with open(DATA_FILE_NAME, 'wb') as f:
        data = {}
        pickle.dump(data, f)


def update_data():
    with open(DATA_FILE_NAME, 'wb') as f:
        pickle.dump(data, f)


logger = logging.getLogger('vk-raid-defender')
logger.setLevel(logging.INFO)
terminal_logger = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s.%(msecs).03d] %(message)s", datefmt="%H:%M:%S")
terminal_logger.setFormatter(formatter)
logger.addHandler(terminal_logger)
logger.propagate = False


def start_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(LOGO + '\n\n')


def ask_yes_or_no(question, true_answer='y', false_answer='n', default_answer='', default=True):
    true_answer = true_answer.lower()
    false_answer = false_answer.lower()
    default_answer = default_answer.lower()

    output = question.strip() + ' (' + (true_answer.upper() + '/' + false_answer if default else
                                        true_answer + '/' + false_answer.upper()) + '): '

    answer = None
    while answer not in (true_answer, false_answer, default_answer):
        answer = input(output).lower()

    if answer == true_answer:
        return True
    if answer == false_answer:
        return False

    return default


class VkSession(VkApi):
    def __init__(self, token, *args, **kwargs):
        super().__init__(*args, token=token, **kwargs)

        self.vk = self.get_api()

    def start(self):
        start_screen()

        chat_ids = data.get('chat_ids')
        objectives = data.get('objectives')

        if chat_ids is None or objectives is None or not ask_yes_or_no('использовать ранее сохранённые данные для работы?'):
            chat_ids = list(map(int, input('введи айди конф, в которых нужно защищать рейдеров, через пробел: ').split()))
            objectives = list(map(int, input('введи айди защищаемых рейдеров: ').split()))

            if ask_yes_or_no('сохранить введённые данные для следующих сессий?'):
                data['chat_ids'] = chat_ids
                data['objectives'] = objectives
                update_data()

        self._chat_ids = chat_ids
        self._objectives = objectives

        start_screen()
        self.listen()

    def listen(self):
        logger.info('начинаю приём сообщений')

        limit_time = time()
        defend_counter = 0

        polling = VkLongPoll(self)

        try:
            for event in polling.listen():
                if not (event.type == VkEventType.MESSAGE_NEW and
                        event.chat_id is not None and
                        event.chat_id in self._chat_ids and
                        event.to_me):
                    continue

                event_dict = event.raw[7]

                if event_dict.get('source_act') == 'chat_kick_user' and event_dict['source_mid'] != event_dict['from']:
                    user_victim = int(event_dict['source_mid'])
                    if user_victim in self._objectives:

                        if time() - limit_time > 1:
                            limit_time = time()
                            defend_counter = 0

                        elif defend_counter >= 3:
                            continue

                        try:
                            self.vk.messages.addChatUser(chat_id=event.chat_id, user_id=user_victim)
                            defend_counter += 1
                            logger.info(f'{user_victim} был возвращён в конфу "{event.subject}"')
                        except Exception as e:
                            logger.error(f'не удалось вернуть {user_victim} в конфу "{event.subject}": "{e}"')

        except Exception as e:
            start_screen()
            logger.critical('произошла критическая ошибка, перезапускаюсь', exc_info=True)

        self.listen()


def authorize():
    print('для работы vk-raid-defender необходима авторизация')

    token = data.get('token')
    proxies = data.get('proxies')

    if token is None or not ask_yes_or_no('использовать ранее сохранённые данные для авторизации?'):
        print('\nhttps://oauth.vk.com/authorize?client_id=6020061&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=69632&response_type=token\n')

        token = None
        while token is None:
            user_input = getpass('перейди по ссылке выше в любом веб-браузере, авторизируйся и вставь адресную строку веб-страницы, на которую было осуществлено перенаправление: ')
            token = re.search(r'(?:.*access_token=)?([a-f0-9]+).*', user_input)

        token = token.group(1)

        proxy = input('введи адрес прокси-сервера при необходимости его использования: ')
        while proxy and not re.match(r'(localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d{1,5}', proxy):
            proxy = input('неверный формат адреса сервера, попробуй ещё раз: ')

        if proxy:
            if ask_yes_or_no('использовать протокол socks5 вместо http?'):
                proxies = {
                    'http': f'socks5://{proxy}',
                    'https': f'socks5://{proxy}'
                }
            else:
                proxies = {
                    'http': f'http://{proxy}',
                    'https': f'https://{proxy}'
                }
        else:
            proxies = None

        if ask_yes_or_no('сохранить введённые данные для следующих сессий?'):
            data['token'] = token
            data['proxies'] = proxies
            update_data()

    session = VkSession(token, proxies=proxies)
    session.start()


def main():
    try:
        authorize()
    except KeyboardInterrupt:
        print()
        sys.exit()


if __name__ == "__main__":
    main()
