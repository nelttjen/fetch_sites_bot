from aiogram import types
from bot.bot_actions import check_user_access


def login_required(func):
    async def wraps(message: types.Message):
        if not check_user_access(message.from_user.id):
            await message.reply('Доступ запрещен', reply_markup=types.ReplyKeyboardRemove())
            return
        await func(message)

    return wraps


def login_required_state(func):
    async def wraps(message: types.Message, state):
        if not check_user_access(message.from_user.id):
            await message.reply('Доступ запрещен', reply_markup=types.ReplyKeyboardRemove())
            return
        await func(message, state)

    return wraps
