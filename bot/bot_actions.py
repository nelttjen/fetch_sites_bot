import asyncio

from aiogram import types

from .bot_core import DEFAULT_USERS
from .fetch_modules import *


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


class Fetches:
    @staticmethod
    async def create_task_fetch(running, check_id, user_id, bot, name="") -> str:
        if running[check_id]['is_running']:
            if user_id not in running[check_id]['users']:
                running[check_id]['users'].append(user_id)
            return f'Проверка {name} уже запущена. Вы получите файл по окончанию проверки'

        operations = {
            1: Fetches.fetch_1,
            2: Fetches.fetch_2,
            3: Fetches.fetch_3,
            4: Fetches.fetch_4,
            5: Fetches.fetch_5,
            6: Fetches.fetch_6,
            7: Fetches.fetch_7,
            8: Fetches.fetch_8,
        }
        func = operations.get(check_id)
        if not func:
            return f'{name} - Неизвестная операция'
        asyncio.create_task(func(check_id, bot, running))
        running[check_id] = {
            'is_running': True,
            'users': [user_id, ]
        }
        return f'Проверка {name} создана, вы получите результат по окончанию'

    @staticmethod
    async def fetch_base(check_id, bot, running, __class, name=''):
        fetch_task = __class(bot=bot, running=running, check_id=check_id)
        result = await fetch_task.execute()
        if not result:
            for user in running[check_id]['users']:
                await bot.send_message(user, f'При проверке {name} произошла ошибка, попробуйте ещё раз')
            return
        running[check_id]['is_running'] = False
        running[check_id]['users'] = []

    @staticmethod
    async def fetch_1(check_id, bot, running):
        await Fetches.fetch_base(check_id, bot, running, Fetch_mintmanga, name='mintmanga')

    @staticmethod
    async def fetch_2(check_id, bot, running):
        await Fetches.fetch_base(check_id, bot, running, Fetch_readmanga, name='readmanga')

    @staticmethod
    async def fetch_3(check_id, bot, running):
        """TODO: mangalib CloudFlare protection, through non-async selenium"""
        await Fetches.fetch_base(check_id, bot, running, Fetch_mangalib, name='mangalib')

    @staticmethod
    async def fetch_4(check_id, bot, running):
        """TODO: yaoillib CloudFlare protection, through non-async selenium"""
        await Fetches.fetch_base(check_id, bot, running, Fetch_yaoilib, name='yaoilib')

    @staticmethod
    async def fetch_5(check_id, bot, running):
        await Fetches.fetch_base(check_id, bot, running, Fetch_newmanga, name='newmanga')

    @staticmethod
    async def fetch_6(check_id, bot, running):
        await Fetches.fetch_base(check_id, bot, running, Fetch_mangachan, name='mangachan')

    @staticmethod
    async def fetch_7(check_id, bot, running):
        await Fetches.fetch_base(check_id, bot, running, Fetch_mangahub, name='mangachan')

    @staticmethod
    async def fetch_8(check_id, bot, running):
        await Fetches.fetch_base(check_id, bot, running, Fetch_mangaovh, name='mangachan')