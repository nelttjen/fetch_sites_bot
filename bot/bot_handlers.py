import asyncio
import logging

from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from .bot_actions import add_user, default_running_dict, Fetches
from .bot_buttons import get_start_keyboard, get_cancel_keyboard
from .bot_core import dispatcher, bot, DEFAULT_USERS
from .bot_decorators import login_required, login_required_state
from .fetch_modules.Fetch_mintmanga import Fetch_1


class States(StatesGroup):
    id_wait = State()


running = default_running_dict()


@dispatcher.message_handler(commands='start', state='*')
@login_required
async def start(message: types.Message):
    await message.reply('Вы авторизованы!', reply_markup=get_start_keyboard())


@dispatcher.message_handler(commands='cancel', state='*')
@dispatcher.message_handler(Text('отмена', ignore_case=True), state='*')
@login_required_state
async def cancel_inputs(message: types.Message, state: FSMContext):
    if await state.get_state() is not None:
        await state.finish()
    await message.reply('Главное меню', reply_markup=get_start_keyboard())


@dispatcher.message_handler(commands='add_user', state='*')
@dispatcher.message_handler(Text(equals='Добавить пользователя в бота', ignore_case=True), state='*')
@login_required
async def new_user_call(message: types.Message):
    if str(message.from_user.id) not in DEFAULT_USERS.split(';'):
        await message.reply('Эта функция вам недоступна. Свяжитесь с администраторами бота.')
        return
    await States.id_wait.set()
    await message.reply('Добавить пользователя по ID\n\nID можно узнать: @getmyid_bot, @username_to_id_bot',
                        reply_markup=get_cancel_keyboard())


@dispatcher.message_handler(state=States.id_wait)
@login_required_state
async def add_by_user_id(message: types.Message, state: FSMContext):
    try:
        add_user(int(message.text))
        await state.finish()
        await message.reply('Пользователь добавлен.', reply_markup=get_start_keyboard())
    except ValueError:
        await message.reply('ID должно быть числом')


@dispatcher.message_handler(commands='/fetch_1', state='*')
@dispatcher.message_handler(commands='/fetch_2', state='*')
@dispatcher.message_handler(commands='/fetch_3', state='*')
@dispatcher.message_handler(commands='/fetch_4', state='*')
@dispatcher.message_handler(commands='/fetch_5', state='*')
@dispatcher.message_handler(commands='/fetch_6', state='*')
@dispatcher.message_handler(commands='/fetch_7', state='*')
@dispatcher.message_handler(commands='/fetch_8', state='*')
@dispatcher.message_handler(commands='/fetch_9', state='*')
@dispatcher.message_handler(Text(equals='mintmanga.live', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='readmanga.io', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='mangalib.me', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='yaoilib.me', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='newmanga.org', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='mangachan.ru', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='mangahub.ru', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='manga.ovh', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='Все', ignore_case=True), state='*')
@login_required
async def method_call(message: types.Message):
    all_operations = {
        'mintmanga.live': 1,
        'readmanga.io': 2,
        'mangalib.me': 3,
        'yaoilib.me': 4,
        'newmanga.org': 5,
        'mangachan.ru': 6,
        'mangahub.ru': 7,
        'manga.ovh': 8,
        'Все': 9
    }
    if message.text.startswith('/fetch_'):
        check_id = int(message.text.replace('/fetch_', ''))
    else:
        check_id = all_operations[message.text]
    user_id = message.from_user.id

    global running
    result = await Fetches.create_task_fetch(running, check_id, user_id, message, bot)
    await message.reply(result)
