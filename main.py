import os.path

from src.CommandHandler import CommandHandler, get_settings

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

TOKEN = get_settings('token')
GROUP_ID = get_settings('group_id')

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

longpoll = VkLongPoll(vk_session, group_id=GROUP_ID)


def main():

    command_handler = CommandHandler(vk, vk_session, get_settings('group_id'))

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            command_handler.command_executor(event.user_id, event.text.lower())


if __name__ == '__main__':
    if not os.path.exists('DB.json'):
        with open('DB.json', 'w') as f:
            f.write('{}')
    try:
        main()
    except KeyboardInterrupt:
        print('Завершение работы.')
