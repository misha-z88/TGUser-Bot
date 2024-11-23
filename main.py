import json
import os
import pytz
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import BadRequest
from config import API_ID, API_HASH, WEATHER_API_KEY
from function import gemini_response, g4f_response
import requests

# Инициализация клиента
app = Client("mybot", api_id=API_ID, api_hash=API_HASH)

# Параметры
allowed_user_ids = [2161024343, 2244396277, 2236646819, 1679002620]
context_file = "context.json"
prefix_file = "prefix.json"
available_models = ["g4f", "gemini", "meta"]

# Функция для получения текущего времени в МСК
def get_time_in_msk():
    return datetime.now(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")

# Загрузка контекста
def load_context():
    if os.path.exists(context_file):
        with open(context_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Сохранение контекста
def save_context(context):
    with open(context_file, "w", encoding="utf-8") as f:
        json.dump(context, f, ensure_ascii=False, indent=4)

# Загрузка префикса
def load_prefix():
    if os.path.exists(prefix_file):
        with open(prefix_file, "r", encoding="utf-8") as f:
            return json.load(f).get("prefix", "/")
    return "/"

# Сохранение префикса
def save_prefix(prefix):
    with open(prefix_file, "w", encoding="utf-8") as f:
        json.dump({"prefix": prefix}, f, ensure_ascii=False, indent=4)

# Обновление контекста пользователя
def update_user_context(user_id, message):
    context = load_context()
    if user_id not in context:
        context[user_id] = {"messages": [], "model": "gemini"}
    context[user_id]["messages"].append(message)
    if len(context[user_id]["messages"]) > 10:
        context[user_id]["messages"].pop(0)
    save_context(context)

# Получение текущей модели пользователя
def get_user_model(user_id):
    context = load_context()
    return context.get(user_id, {}).get("model", "gemini")

# Установка модели пользователя
def set_user_model(user_id, model_name):
    if model_name in available_models:
        context = load_context()
        if user_id not in context:
            context[user_id] = {"messages": []}
        context[user_id]["model"] = model_name
        save_context(context)
        return True
    return False

# Генерация ответа от ИИ
async def get_ai_response(model, message, user_id):
    try:
        context = load_context()
        user_context = context.get(user_id, {}).get("messages", [])
        full_message = "\n".join(user_context) + f"\n{message}"
        
        if model == "g4f":
            return g4f_response(full_message)
        elif model == "gemini":
            return gemini_response(full_message)
        elif model == "meta":
            return "Модель Meta временно недоступна."
        return "Неизвестная модель."
    except Exception as e:
        print(f"Ошибка в get_ai_response: {e}")
        return "Произошла ошибка при генерации ответа."

# Команда /help
@app.on_message(filters.command("help"))
async def help_handler(client, message: Message):
    prefix = load_prefix()
    help_text = f"""
Доступные команды:
{prefix}help - Справка.
{prefix}time - Текущее время в МСК.
{prefix}info - Информация о пользователе.
{prefix}set_model <model_name> - Установка модели (g4f, gemini, meta).
{prefix}gpt <текст> - Генерация ответа.
{prefix}set_prefix <символ> - Установить новый префикс.
{prefix}weather <город> - Узнать погоду в указанном городе.
"""
    await message.reply(help_text)

# Команда /info
@app.on_message(filters.command("info"))
async def info_handler(client, message: Message):
    user = await client.get_users(message.from_user.id)
    info_text = (
        f"Ваш ID: {user.id}\n"
        f"Ваше имя: {user.first_name}\n"
        f"Ваш username: {user.username or 'Неизвестен'}\n"
        f"Дата создания аккаунта: {user.dc_id}\n"
        f"Бот: {'Да' if user.is_bot else 'Нет'}"
    )
    await message.reply(info_text)

# Команда /time
@app.on_message(filters.command("time"))
async def time_handler(client, message: Message):
    await message.reply(f"Текущее время в МСК: {get_time_in_msk()}")

# Команда /set_model
@app.on_message(filters.command("set_model"))
async def set_model_handler(client, message: Message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❗ Укажите модель.")
        return
    model_name = args[1].strip().lower()
    if set_user_model(user_id, model_name):
        await message.reply(f"Модель изменена на {model_name}.")
    else:
        await message.reply("❗ Неизвестная модель. Доступные: g4f, gemini, meta.")

# Команда /set_prefix
@app.on_message(filters.command("set_prefix"))
async def set_prefix_handler(client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❗ Укажите новый префикс.")
        return
    new_prefix = args[1].strip()
    save_prefix(new_prefix)
    await message.reply(f"Префикс изменён на {new_prefix}")

# Команда /gpt
@app.on_message(filters.command(["гпт", "gpt"]))
async def gpt_handler(client, message: Message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❗ Укажите текст для обработки.")
        return
    req_text = args[1]
    update_user_context(user_id, req_text)
    model = get_user_model(user_id)
    response_text = await get_ai_response(model, req_text, user_id)
    await message.reply(response_text, reply_to_message_id=message.id)  # Используем message.id


# Команда /weather
@app.on_message(filters.command("weather"))
async def weather_handler(client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❗ Укажите город.")
        return
    city = args[1].strip()
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&lang=ru&units=metric"
        response = requests.get(url).json()
        if response.get("cod") != 200:
            await message.reply(f"Ошибка: {response.get('message', 'Город не найден')}")
            return
        weather = response["weather"][0]["description"]
        temp = response["main"]["temp"]
        await message.reply(f"Погода в {city}: {weather}, температура: {temp}°C")
    except Exception as e:
        print(f"Ошибка получения погоды: {e}")
        await message.reply("Не удалось получить данные о погоде.")

if __name__ == "__main__":
    print("Бот запущен...")
    app.run()
