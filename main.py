
from aiogram import Bot, Dispatcher, types, F
import logging
import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from weather_app import get_weather_data, format_forecast, get_location_key_for_city
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

bot_token = '7739889395:AAFNe9GBjetDwR9aqQKXVtPGOqVpm2zW-fg'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=bot_token)
dp = Dispatcher()

class WeatherStates(StatesGroup):
    waiting_for_city = State()
# старт
@dp.message(F.text == '/start')
async def send_welcome(message: types.Message):
    button_for_help = KeyboardButton(text='/help')
    button_for_weather = KeyboardButton(text='/weather')
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_for_help], [button_for_weather]],
        resize_keyboard=True
    )
    await message.answer(
        'Привет! Я телеграм бот для погоды. Я могу предоставить прогноз погоды для вашего города.',
        reply_markup=reply_keyboard
    )
# помощь
@dp.message(F.text == '/help')
async def send_help(message: types.Message):
    await message.answer('Список доступных команд:\n'
                         '/start - Начать общение с ботом\n'
                         '/help - Получить помощь\n'
                         '/weather - Запросить прогноз погоды')
# погода
@dp.message(F.text == '/weather')
async def send_weather(message: types.Message):
    button_for_3_days = KeyboardButton(text='Прогноз на 3 дня')
    button_for_5_days = KeyboardButton(text='Прогноз на 5 дней')
    reply_keyboard_for_days = ReplyKeyboardMarkup(
        keyboard=[[button_for_3_days], [button_for_5_days]],
        resize_keyboard=True
    )
    await message.answer('Выберите промежуток для прогноза погоды:', reply_markup=reply_keyboard_for_days)

@dp.message(F.text == 'Прогноз на 3 дня')
async def prognoz_3_days(message: types.Message, state: FSMContext):
    await state.set_data({'days': 3})
    await state.set_state(WeatherStates.waiting_for_city)
    await message.answer('Введите 2 города формата: \nМосква, Санкт-петербург')


@dp.message(F.text == 'Прогноз на 5 дней')
async def prognoz_5_days(message: types.Message, state: FSMContext):
    await state.set_data({'days': 5})
    await state.set_state(WeatherStates.waiting_for_city)
    await message.answer('Введите 2 города формата: \nМосква, Санкт-петербург')


@dp.message(WeatherStates.waiting_for_city)
async def process_cities(message: types.Message, state: FSMContext):
    cities = message.text.split(',')
    if len(cities) != 2:
        await message.answer("Пожалуйста, введите два города, разделенные запятой.")
        return
    city1 = cities[0].strip()
    city2 = cities[1].strip()
    user_data = await state.get_data()
    days = user_data.get('days', 3)
    try:
        for city in [city1, city2]:
            location_key = get_location_key_for_city(city)
            if not location_key:
                await message.answer(f"Не удалось найти город {city}")
                continue
            weather_data = get_weather_data(location_key, days)
            if not weather_data:
                await message.answer(f"Не удалось получить данные о погоде для {city}")
                continue
            formatted_forecast = format_forecast(weather_data)
            result = f"Прогноз погоды для {city} на {days} дней:\n\n"
            for day in formatted_forecast:
                result += f"Дата: {day['date']}\n"
                result += f"Температура: от {day['min_temp']}°C до {day['max_temp']}°C\n"
                result += f"Днем: {day['day_condition']}\n"
                result += f"Ночью: {day['night_condition']}\n\n"
            await message.answer(result)
    except Exception as e:
        await message.answer(f"Произошла ошибка при получении прогноза погоды: {str(e)}")
    await state.clear()

async def main():
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())