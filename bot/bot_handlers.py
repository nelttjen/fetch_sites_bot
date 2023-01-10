import asyncio
import logging

from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from .bot_actions import add_user, default_running_dict, Fetches
from .bot_buttons import get_start_keyboard, get_cancel_keyboard, get_agree_keyboard
from .bot_core import dispatcher, bot, DEFAULT_USERS
from .bot_decorators import login_required, login_required_state


class States(StatesGroup):
    id_wait = State()

    mangalib = State()
    yaoilib = State()
    hentailib = State()
    shikimori = State()


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
@dispatcher.message_handler(commands='/fetch_10', state='*')
@dispatcher.message_handler(Text(equals='mintmanga.live', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='readmanga.live', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='mangalib.me', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='yaoilib.me', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='newmanga.org', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='mangachan.ru', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='mangahub.ru', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='manga.ovh', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='hentailib.me', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='shikimori.one', ignore_case=True), state='*')
@dispatcher.message_handler(Text(equals='Все', ignore_case=True), state='*')
@login_required
async def method_call(message: types.Message):
    all_operations = {
        'mintmanga.live': 1,
        'readmanga.live': 2,
        'mangalib.me': 3,
        'yaoilib.me': 4,
        'newmanga.org': 5,
        'mangachan.ru': 6,
        'mangahub.ru': 7,
        'manga.ovh': 8,
        'hentailib.me': 9,
        'shikimori.one': 10,
        'Все': 11
    }
    if message.text.startswith('/fetch_'):
        check_id = int(message.text.replace('/fetch_', ''))
    else:
        check_id = all_operations[message.text]
    user_id = message.from_user.id

    if check_id in (3, 4, 9):
        if check_id == 3:
            state = States.mangalib
        if check_id == 4:
            state = States.yaoilib
        if check_id == 9: 
            state = States.hentailib
        await message.reply(f'Вы уверены, что хотите запустить проверку {message.text}? '
                            f'Во время выполнения бот может подвисать и долго не реагировать на сообщения.'
                            f'Проверка происходит драйвером Chrome, проверьте, чтобы он был установлен и помещен в '
                            f'корень приложения в папку driver. Драйвер запускается в headless режиме, окно браузера '
                            f'не будет создано, вы можете продолжать пользоваться компьютером',
                            reply_markup=get_agree_keyboard())
        await state.set()
        return

    global running
    if check_id == 11:
        for key, val in all_operations.items():
            if val == 11 or val in [3, 4, 9]:
                continue
            result = await Fetches.create_task_fetch(running, val, user_id, bot, name=key)
            await message.reply(result)
    else:
        result = await Fetches.create_task_fetch(running, check_id, user_id, bot, name=message.text)
        await message.reply(result)


@dispatcher.message_handler(state=States.mangalib)
@login_required_state
async def execute_mangalib(message: types.Message, state: FSMContext):
    if message.text not in ('Подтвердить', 'Вернуться назад'):
        await message.reply('Неизвестная операция')
        return
    if message.text == 'Вернуться назад':
        await message.reply('Главное меню', reply_markup=get_start_keyboard())
        return
    await state.finish()
    result = await Fetches.create_task_fetch(running, 3, message.from_user.id, bot, name='mangalib.me')
    await message.reply(result, reply_markup=get_start_keyboard())


@dispatcher.message_handler(state=States.yaoilib)
@login_required_state
async def execute_mangalib(message: types.Message, state: FSMContext):
    if message.text not in ('Подтвердить', 'Вернуться назад'):
        await message.reply('Неизвестная операция')
        return
    if message.text == 'Вернуться назад':
        await message.reply('Главное меню', reply_markup=get_start_keyboard())
        return
    await state.finish()
    result = await Fetches.create_task_fetch(running, 4, message.from_user.id, bot, name='yaoilib.me')
    await message.reply(result, reply_markup=get_start_keyboard())

@dispatcher.message_handler(state=States.hentailib)
@login_required_state
async def execute_mangalib(message: types.Message, state: FSMContext):
    if message.text not in ('Подтвердить', 'Вернуться назад'):
        await message.reply('Неизвестная операция')
        return
    if message.text == 'Вернуться назад':
        await message.reply('Главное меню', reply_markup=get_start_keyboard())
        return
    await state.finish()
    result = await Fetches.create_task_fetch(running, 9, message.from_user.id, bot, name='hentailib.me')
    await message.reply(result, reply_markup=get_start_keyboard())