from aiogram.dispatcher.filters.state import StatesGroup, State

class WeatherState(StatesGroup):
    weather = State()
    # own_weather = State()