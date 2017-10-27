import sys

try:
    from vk_api import VkApi
except ImportError:
    sys.exit('для работы vk-raid-defender необходима библиотека vk_api')

from vk_api.longpoll import VkLongPoll, VkEventType

from .settings import DATA_FILE_NAME, CLIENT_ID
from .logger import logger

import pickle
from time import time


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


class VkRaidDefender(VkApi):
    def __init__(self, token, proxies=None, *args, **kwargs):
        super().__init__(*args, token=token, **kwargs)
        self.http.proxies = proxies
        self.vk = self.get_api()
        self.polling = VkLongPoll(self)
        self._chat_ids = []
        self._objectives = []

    def listen(self):
        limit_time = time()
        defend_counter = 0

        for event in self.polling.listen():
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
                        logger.info('{} был возвращён в конфу "{}"'.format(user_victim, event.subject))
                    except Exception as e:
                        logger.error('не удалось вернуть {} в конфу "{}": "{}"'.format(user_victim, event.subject, str(e)))
