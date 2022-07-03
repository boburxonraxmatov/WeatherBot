import sqlite3
from datetime import datetime

import requests
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Хранилице в памяти, куда будем сохранять
from aiogram.dispatcher import FSMContext  # Адрес на локальное хранилище - Оперативка
from aiogram.dispatcher.filters.state import State, StatesGroup  # Группа вопросов и вопросы
from aiogram.types import Message

from configs import *

# import psycopg2

storage = MemoryStorage()  # Открываем хранилице
bot = Bot(token=TOKEN, parse_mode='HTML')  # Подключитесь к боту в телеграме, и редактирование в виде HTML

dp = Dispatcher(bot, storage=storage)  # Объект диспейчера, который будет следить за ботом, сохраняем хранилице


class GetWeather(StatesGroup):
    city = State()


@dp.message_handler(commands=['start', 'about', 'help'])  # , 'about', 'help'
async def command_start(message: Message):

    if message.text == '/start':
        await message.answer(f'Здравствуйте <b>{message.from_user.full_name}</b>. Я бот чтобы рассказать вам погоду')
        await get_first_city(message)
    elif message.text == '/about':
        await message.answer(f'''Данный бот был создан в <i>домашних условиях</i>''')
    elif message.text == '/help':
        await message.answer(
            '''При возникших идеях или проблемах пишите сюда: <tg-spoiler>@boburxon_raxmatov</tg-spoiler>''')


async def get_first_city(message: Message):
    await GetWeather.city.set()
    await message.answer('Введите город у которого хотите узнать погоду: ')


@dp.message_handler(state=GetWeather.city)
async def show_city_weather(message: Message, state: FSMContext):
    # await bot.send_message(message.chat.id, f"{message.text}")
    try:
        parameters['q'] = message.text

        data = requests.get('https://api.openweathermap.org/data/2.5/weather', params=parameters).json()
        temp = data['main']['temp']
        wind = data['wind']['speed']
        name = data['name']
        description = data['weather'][0]['description']
        timezone = data['timezone']
        sunrise = datetime.utcfromtimestamp(data['sys']['sunrise'] + timezone).strftime('%H:%M:%S')  # %Y:%M:%D
        sunset = datetime.utcfromtimestamp(data['sys']['sunset'] + timezone).strftime('%H:%M:%S')
        await bot.send_message(message.chat.id, f'''В городе {name} сейчас {description}
Температура: {temp} °C
Скорость ветра: {wind} м/с
Рассвет: {sunrise} часов
Закат: {sunset} часов''')

        database = sqlite3.connect('ls5.db')
        cursor = database.cursor()
        cursor.execute('''
            INSERT INTO weather(temp, wind, name, description, sunrise, sunset)
            VALUES (?,?,?,?,?,?);
            ''', (temp, wind, name, description, sunrise, sunset))
        database.commit()
        database.close()
        await state.finish()
        await bot.send_message(message.chat.id, f"""Выбери команду
/start
/about
/help
""")

    except Exception as e:
        print(e)
        await bot.send_message(message.chat.id, 'Не верно указан город, Попробуй снова!!!')
        await get_first_city(message)

# def print(customers):
#     pass
executor.start_polling(dp)


# while True:
#     city = input('Введите город, в котором хотите узнать погоду: ')
#     parameters['q'] = city
#     try:
#         data = requests.get('https://api.openweathermap.org/data/2.5/weather', params=parameters).json()
#         temp = data['main']['temp']
#         wind = data['wind']['speed']
#         name = data['name']
#         description = data['weather'][0]['description']
#         timezone = data['timezone']
#         sunrise = datetime.utcfromtimestamp(data['sys']['sunrise'] + timezone).strftime('%H:%M:%S')  # %Y:%M:%D
#         sunset = datetime.utcfromtimestamp(data['sys']['sunset'] + timezone).strftime('%H:%M:%S')
#         print(f'''В городе \033[34m{name}\033[0m сейчас {description}
# Температура \{temp} °C
# Скорость ветра {wind} м/с
# Рассвет {sunrise} часов
# Закат {sunset} часов''')
#
#         database = sqlite3.connect('ls5.db')
#         cursor = database.cursor()
#         cursor.execute('''
#         INSERT INTO weather(temp, wind, name, description, sunrise, sunset)
#         VALUES (?,?,?,?,?,?);
#         ''', (temp, wind, name, description, sunrise, sunset))
#         database.commit()
#         database.close()
#
#         # database = psycopg2.connect(
#         #     database='ls5',
#         #     host='localhost',
#         #     user='postgres',
#         #     password='123456'
#         # )
#         #
#         # cursor = database.cursor()
#         #
#         # cursor.execute('''
#         #     INSERT INTO weather(temp, wind, name, description, sunrise, sunset)
#         #     VALUES (%s, %s, %s, %s, %s, %s);
#         #     ''', (temp, wind, name, description, sunrise, sunset))
#         # database.commit()
#         # database.close()
#
#
#     except Exception as e:
#         print(e)
#         print('Не верно указан город, Попробуй снова!!!')
# from countryinfo import CountryInfo

# while True:
#     user_country = input('Введите страну: ')
#     country = CountryInfo(user_country)
#     data = country.info()
#     try:
#         name = data['name']
#         area = data['area']
#         population = data['population']
#         region = data['region']
#         subregion = data['subregion']
#         timezones = data['timezones']
#         print(
#             f'''В городе {name}, площадь которой {area} и численность {population}, который находится в {region} в {subregion}, часовой пояс {timezones}''')
#     except Exception as e:
#         print('Что то не то!!!')


