import asyncio
import requests
import pyquery as pq


from aiogram import types

from .bot_core import DEFAULT_USERS
from .fetch_modules.Fetch_mintmanga import Fetch_1


def add_user(new_user: int) -> None:
    user_list = get_current_user_list()
    user_list.append(str(new_user))
    with open('users.txt', 'w', encoding='utf-8') as out:
        out.write(';'.join(user_list))


def get_current_user_list():
    with open('users.txt', 'r', encoding='utf-8') as file:
        user_list = file.read().split(';')
    return user_list


def check_user_access(user_id: int) -> bool:
    return str(user_id) in get_current_user_list() or str(user_id) in DEFAULT_USERS.split(';')


def default_running_dict():
    new_dict = dict()
    for i in range(1, 10):
        new_dict[i] = {
            'is_running': False,
            'users': []
        }
    return new_dict


async def get_links_query(endpoint, _class) -> list:
    response = requests.get(endpoint)
    if response.status_code != 200:
        return []
    query = pq.PyQuery(response.text)
    elements = query.find(_class).items()
    return [elem.attr('href') for elem in elements]


async def fetch_1(_dict, message, bot):
    class_fetch_1 = Fetch_1(_dict, message, bot)
    result = await class_fetch_1.execute()
    _dict['is_running'] = False
    _dict['users'] = []
    if not result:
        await message.reply('При проверке mintmanga произошла ошибка, попробуйте ещё раз.')


async def fetch_2(_dict, message, bot):
    pass


async def create_task_fetch(_dict, check_id, user_id, message: types.Message, bot, ) -> str:
    if _dict[check_id]['is_running']:
        if user_id not in _dict[check_id]['users']:
            _dict[check_id]['users'].append(user_id)
        return 'Проверка уже запущена. Вы получите файл по окончанию проверки'

    operations = {
        1: fetch_1,
        2: fetch_2,
    }
    func = operations.get(check_id)
    if not func:
        return 'Неизвестная операция'
    asyncio.create_task(func(_dict, message, bot))
    _dict[check_id] = {
        'is_running': True,
        'users': [user_id, ]
    }
    return 'Проверка создана, вы получите результат по окончанию'

