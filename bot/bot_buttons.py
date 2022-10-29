from aiogram import types


def get_start_keyboard():
    keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('Добавить пользователя в бота')
    keyb.add(button)

    row_1_button_1 = types.KeyboardButton('mintmanga.live')
    row_1_button_2 = types.KeyboardButton('readmanga.live')
    row_1_button_3 = types.KeyboardButton('mangalib.me')
    row_2_button_1 = types.KeyboardButton('yaoilib.me')
    row_2_button_2 = types.KeyboardButton('newmanga.org')
    row_2_button_3 = types.KeyboardButton('mangachan.ru')
    row_3_button_1 = types.KeyboardButton('mangahub.ru')
    row_3_button_2 = types.KeyboardButton('manga.ovh')
    row_3_button_3 = types.KeyboardButton('Все')

    keyb.row(row_1_button_1, row_1_button_2, row_1_button_3)
    keyb.row(row_2_button_1, row_2_button_2, row_2_button_3)
    keyb.row(row_3_button_1, row_3_button_2, row_3_button_3)

    return keyb


def get_cancel_keyboard():
    keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel = types.KeyboardButton('Отмена')
    keyb.add(cancel)
    return keyb