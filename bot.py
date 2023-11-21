from aiogram import Bot, types, Dispatcher, executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, ReplyKeyboardRemove

from dotenv import load_dotenv
import logging, requests
import os

from custom_state import WeatherState
from buttons import button, location_markup

OPENWEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather'
OPENWEATHER_GEOCODER_URL = 'http://api.openweathermap.org/geo/1.0/reverse'
load_dotenv('.env')

bot = Bot(os.environ.get('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

@dp.callback_query_handler(lambda call:call)
async def buttons(call):
    if call.data == 'start':
        await hello(call.message)
    elif call.data == 'own_weather':
        await user_location(call.message)
    elif call.data == 'weather':
        await weather(call.message)



@dp.message_handler(commands=['start'])
async def hello(message:types.Message):
    await message.answer(f'Здравствуйте {message.from_user.full_name}')
    await message.answer(f'Этот бот подскажет вам погоду в том или ином городе')
    await message.answer(f'Для начала работы нажмите на кнопку ниже', reply_markup=button)

@dp.message_handler(commands=['weather'])
async def weather(message:types.Message):
    await message.answer('Введите название города погоду которого хотите узнать: ')
    await WeatherState.weather.set()

@dp.message_handler(state=WeatherState.weather)
async def get_weather(message:types.Message, state:FSMContext):
    city = message.text

    try:
        params = {
            'q': city,
            'appid': os.environ.get('WEATHER_TOKEN'),
            'units': 'metric',
            'lang' : 'ru'
        }
        response = requests.get(OPENWEATHER_API_URL, params=params)
        weather_data = response.json()

        if 'cod' in weather_data and weather_data['cod'] == '404':
            await message.reply("Город не найден.")
            return

        if 'main' not in weather_data:
            logging.error(f"Ответ не содержит ключа 'main': {weather_data}")
            await message.reply("Произошла ошибка при получении погоды.")
            return

        temperature = weather_data['main'].get('temp')
        if temperature is None:
            logging.error(f"Ответ не содержит ключа 'temp' в 'main': {weather_data}")
            await message.reply("Произошла ошибка при получении погоды.")
            return

        description = weather_data['weather'][0]['description']
        weather_text = f"Погода в городе {city}: {temperature}°C, {description}."
        await message.reply(weather_text, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logging.exception(f"Ошибка при получении погоды: {e}")
        await message.reply("Произошла ошибка при получении погоды.")
    
@dp.message_handler(commands='get_location')
async def user_location(message:types.Message):
    await message.answer('Нажмите на кнопку ниже и бот покажет покажет данные погоды рядом с вами', reply_markup=location_markup)
    await WeatherState.weather.set()
    
@dp.message_handler(state=WeatherState.weather, content_types=types.ContentType.LOCATION)
async def get_own_weather(message: types.Message, state: FSMContext):
    longitude = message.location.longitude
    latitude = message.location.latitude

    geocoder_params = {
        'lon': longitude,
        'lat': latitude,
        'appid': os.environ.get('WEATHER_TOKEN')
    }

    try:
        response = requests.get(OPENWEATHER_GEOCODER_URL, params=geocoder_params)
        geocoder_data = response.json()

        city = geocoder_data[0]['local_names'].get('ru', '')

        params = {
            'lon': longitude,
            'lat': latitude,
            'appid': os.environ.get('WEATHER_TOKEN'),
            'units': 'metric',
            'lang' : 'ru',
        }

        response = requests.get(OPENWEATHER_API_URL, params=params)
        weather_data = response.json()
        if 'cod' in weather_data and weather_data['cod'] == '404':
            await message.reply("Город не найден.")
            return

        if 'main' not in weather_data:
            logging.error(f"Ответ не содержит ключа 'main': {weather_data}")
            await message.reply("Произошла ошибка при получении погоды.")
            return

        temperature = weather_data['main'].get('temp')
        if temperature is None:
            logging.error(f"Ответ не содержит ключа 'temp' в 'main': {weather_data}")
            await message.reply("Произошла ошибка при получении погоды.")
            return

        description = weather_data['weather'][0]['description']
        weather_text = f"Погода в городе {city}: {temperature}°C, {description}."
        await message.reply(weather_text, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logging.exception(f"Ошибка при получении погоды: {e}")
        await message.reply("Произошла ошибка при получении погоды.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)