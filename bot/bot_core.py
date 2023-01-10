from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from os import path
from pathlib import Path

try:
    with open('token.txt', 'r', encoding='utf-8') as token_f:
        data = token_f.read()
except FileNotFoundError:
    raise Exception('Please create token.txt file with bot token in core folder')
if not data:
    raise Exception('token.txt file must contain bot token')

bot = Bot(token=data)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)

DEFAULT_USERS = '869415947'

DRIVER_EXECUTABLE_PATH_LINUX = "driver/chromedriver"
DRIVER_EXECUTABLE_PATH_WINDOWS = path.join(Path(__file__).parents[1], 'driver', 'chromedriver.exe')
print(DRIVER_EXECUTABLE_PATH_WINDOWS)

DRIVER_EXECUTABLE_PATH = DRIVER_EXECUTABLE_PATH_WINDOWS
