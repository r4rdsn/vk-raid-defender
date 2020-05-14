from .. import __description__
from ..defender import VkRaidDefender, data, update_data

####################################################################################################
LOGO = '''\
       _                _     _       _       __                _
__   _| | __  _ __ __ _(_) __| |   __| | ___ / _| ___ _ __   __| | ___ _ __
\ \ / / |/ / | '__/ _` | |/ _` |  / _` |/ _ \ |_ / _ \ '_ \ / _` |/ _ \ '__|
 \ V /|   <  | | | (_| | | (_| | | (_| |  __/  _|  __/ | | | (_| |  __/ |
  \_/ |_|\_\ |_|  \__,_|_|\__,_|  \__,_|\___|_|  \___|_| |_|\__,_|\___|_|

by alfred richardsn'''
####################################################################################################

from ..logger import logger
from ..settings import CLIENT_ID

import re
import os
import sys
import webbrowser
from getpass import getpass
from argparse import ArgumentParser

from vk_api.exceptions import ApiError
from requests.exceptions import InvalidSchema, ProxyError


class CLIDefender(VkRaidDefender):
    def run(self, chat_ids, objectives):
        self._chat_ids = chat_ids
        self._objectives = objectives

        start_screen()
        logger.info('начинаю приём сообщений')

        try:
            self.listen()

        except KeyboardInterrupt:
            raise

        except Exception as e:
            start_screen()
            logger.critical('произошла критическая ошибка, перезапускаюсь', exc_info=True)

        self.listen()


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
    elif answer == false_answer:
        return False
    else:
        return default


def register():
    use_webbrowser = ask_yes_or_no('открыть ссылку для авторизации в веб-браузере по умолчанию?')
    print()

    oauth_url = 'https://oauth.vk.com/authorize?client_id={}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=69632&response_type=token'.format(CLIENT_ID)

    if use_webbrowser:
        webbrowser.open(oauth_url, new=2)
        print('в веб-браузере только что была открыта ссылка для авторизации.')
    else:
        print(oauth_url + '\n')
        print('открой в веб-браузере страницу по ссылке выше.')

    token = None
    while token is None:
        user_input = getpass('авторизируйся на открытой странице при необходимости и вставь адресную строку страницы, на которую было осуществлено перенаправление: ')
        token = re.search(r'(?:.*access_token=)?([a-f0-9]+).*', user_input)

    return token.group(1)


def run(proxy=None, chat_ids=[], objectives=[], auto_login=False):
    token = data.get('token')
    proxies = data.get('proxies')

    if not token or (not auto_login and not ask_yes_or_no('использовать ранее сохранённые данные для авторизации?')):
        token = register()
        proxies = None

        IP_ADDRESS = re.compile(r'((socks5://)|(?:https?://))?(localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5})')

        if proxy:
            match = IP_ADDRESS.match(proxy)

        if not proxy or (not match and not auto_login):
            proxy = input('введи адрес прокси-сервера при необходимости его использования: ')
            while proxy:
                match = IP_ADDRESS.match(proxy)
                if match:
                    break
                proxy = input('неверный формат адреса сервера, попробуй ещё раз: ')
            else:
                match = None

        if match:
            protocol, use_socks, ip = match.groups()
            if not protocol:
                use_socks = ask_yes_or_no('использовать протокол socks5 вместо http?') if not auto_login else False

            if use_socks:
                proxies = {'http': 'socks5://' + ip, 'https': 'socks5://' + ip}
            else:
                proxies = {'http': 'http://' + ip, 'https': 'https://' + ip}

        if auto_login or ask_yes_or_no('сохранить введённые данные для следующих сессий?'):
            data['token'] = token
            data['proxies'] = proxies
            update_data()

    start_screen()

    if not chat_ids:
        chat_ids = data.get('chat_ids')
    if not objectives:
        objectives = data.get('objectives')

    if chat_ids is None or objectives is None or (not auto_login and not ask_yes_or_no('использовать ранее сохранённые данные для работы?')):
        chat_ids = list(map(int, input('введи айди конф, в которых нужно защищать рейдеров, через пробел: ').split()))
        objectives = list(map(int, input('введи айди защищаемых рейдеров: ').split()))

        if auto_login or ask_yes_or_no('сохранить введённые данные для следующих сессий?'):
            data['chat_ids'] = chat_ids
            data['objectives'] = objectives
            update_data()

    try:
        defender = CLIDefender(token, proxies=proxies)
    except InvalidSchema:
        sys.exit('необходимо установить дополнительные зависимости для поддержки протокола socks5')
    except ApiError:
        del data['token']
        update_data()
        sys.exit('введённый токен недействителен')
    except ProxyError:
        del data['proxies']
        update_data()
        sys.exit('не удалось подключиться к прокси-серверу')

    defender.run(chat_ids, objectives)


def main():
    parser = ArgumentParser(prog='vk-raid-defender', description=__description__, usage='%(prog)s [опции]', add_help=False)

    group = parser.add_argument_group('опциональные аргументы')
    group.add_argument('-h', '--help', action='help', help='показать это сообщение о помощи и выйти')
    group.add_argument('-l', '--login', action='store_true', help='осуществить автоматическую авторизацию')
    group.add_argument('-p', '--proxy', metavar='proxy_address', help='адрес прокси-сервера')
    group.add_argument('-c', '--chats', type=int, nargs='+', metavar='chat', help='айди конф, в которых нужно защищать рейдеров')
    group.add_argument('-u', '--users', type=int, nargs='+', metavar='user', help='айди защищаемых рейдеров')

    args = parser.parse_args()

    try:
        run(args.proxy, args.chats, args.users, args.login)
    except KeyboardInterrupt:
        print()
        sys.exit()


if __name__ == "__main__":
    main()
