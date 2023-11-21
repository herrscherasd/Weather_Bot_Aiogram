from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

inline_buttons = [
    InlineKeyboardButton('Старт', callback_data='start'),
    InlineKeyboardButton('Узнать погоду у вас', callback_data='own_weather'),
    InlineKeyboardButton('Узнать погоду в каком-либо городе', callback_data='weather'),
]

button = InlineKeyboardMarkup().add(*inline_buttons)

location_button = KeyboardButton('Поделиться местоположением', request_location=True)

location_markup = ReplyKeyboardMarkup().add(location_button)