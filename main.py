
"""
############################################
#                                          #
#            ##   USER BOT   ##            #
#                                          #
#            V0.2.0. BY MIKAYILAZ          #
#                                          # 
#                                          #
############################################

GitHub - https://github.com/mikayilaz 

""" 

# Importing the JSON library to handle configurations and data storage.
import json
# Importing OS library to manage file and directory operations.
import os
# Importing Pytz for timezone handling.
import pytz
# Importing Datetime to handle date and time operations.
from datetime import datetime, timedelta
# Importing Pyrogram for Telegram bot interactions.
from pyrogram import Client, filters
# Importing Pyrogram for Telegram bot interactions.
from pyrogram.types import Message
import requests
import asyncio
from function import gemini_response, g4f_response, chatgpt_response
from config import API_ID, API_HASH
import random
from config import WEATHER_API_KEY  
import yt_dlp
# Importing OS library to manage file and directory operations.
from youtubesearchpython import VideosSearch
# Importing OS library to manage file and directory operations.
import os
import asyncio
# Importing Pyrogram for Telegram bot interactions.
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Инициализация клиента
app = Client("mybot", api_id=API_ID, api_hash=API_HASH)

# Параметры
allowed_user_ids = [] # Ваш юзер-ид и тех кому вы хотите дать "админа" в боте
context_file = "context.json"
prefix_file = "prefix.json"
AVAILABLE_MODELS = ["g4f", "gemini", "chatgpt"]

# Кэш для контекста
context_cache = {}

# Переменная для контроля спама
stop_spam_flag = False
STICKER_ID = ""
WEATHER_URL = "https://api.openweathermap.org/data/2.5/onecall"

# -------------------------------------------------------------------------------------------------
# *** Поиск музыки ***




# Конфигурация yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'nocheckcertificate': True,
    'prefer_ffmpeg': True,
    'keepvideo': False,
    'geo_bypass': True,
}

# Кэш для хранения результатов поиска
search_results_cache = {}

@app.on_message(filters.command("music"))

# Function: async def music_search_handler(client, message: Message):
# Description: Add a description here for the function's purpose.

async def music_search_handler(client, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply(
                "❗ Использование: /music название песни\n"
                "📝 Пример: /music In The End Linkin Park"
            )
            return

        search_query = " ".join(message.command[1:])
        status_msg = await message.reply("🔍 Ищу музыку...")
        
        try:
            videos_search = VideosSearch(search_query, limit=5)
            results = videos_search.result()['result']
        except Exception as search_error:
            await status_msg.edit_text("❌ Ошибка при поиске. Попробуйте позже.")
            return

        if not results:
            await status_msg.edit_text("❌ Ничего не найдено!")
            return

        search_results_cache[message.from_user.id] = results

        response_text = "🎵 Результаты поиска:\n\n"
        for idx, video in enumerate(results, 1):
            duration = video.get('duration', 'N/A')
            if duration == 'N/A':
                duration = '⚠️ Длительность неизвестна'
            
            channel = video.get('channel', {}).get('name', 'Неизвестный исполнитель')
            views = video.get('viewCount', {}).get('text', 'N/A')
            
            response_text += (
                f"{idx}. {video['title']}\n"
                f"👤 {channel} | ⏱ {duration}\n"
                f"👁 {views}\n\n"
            )
        
        response_text += "💡 Чтобы скачать песню, используйте команду:\n/download номер"
        await status_msg.edit_text(response_text)

    except Exception as e:
        await message.reply(f"❗ Произошла ошибка: {str(e)}")

@app.on_message(filters.command("download"))

# Function: async def download_handler(client, message: Message):
# Description: Add a description here for the function's purpose.

async def download_handler(client, message: Message):
    try:
        if len(message.command) != 2:
            await message.reply("❗ Использование: /download номер")
            return

        user_id = message.from_user.id
        if user_id not in search_results_cache:
            await message.reply(
                "❌ Сначала выполните поиск с помощью команды /music\n"
                "🔄 Предыдущие результаты поиска устарели"
            )
            return

        try:
            selection = int(message.command[1])
            if not (1 <= selection <= len(search_results_cache[user_id])):
                await message.reply("❌ Неверный номер. Пожалуйста, выберите число от 1 до 5")
                return
        except ValueError:
            await message.reply("❌ Укажите корректный номер")
            return

        video = search_results_cache[user_id][selection - 1]
        video_url = f"https://www.youtube.com/watch?v={video['id']}"

        status_msg = await message.reply(
            f"⏳ Загружаю: {video['title']}\n"
            "🎵 Пожалуйста, подождите..."
        )

        # Создаем папку для загрузок
        os.makedirs('downloads', exist_ok=True)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                audio_file = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
        except Exception as download_error:
            await status_msg.edit_text(
                f"❌ Ошибка при загрузке:\n"
                f"└ {str(download_error)}\n\n"
                "🔧 Возможные причины:\n"
                "- Видео недоступно\n"
                "- Ограничение по возрасту\n"
                "- Проблемы с подключением"
            )
            return

        try:
            duration = int(info.get('duration', 0))
            await client.send_audio(
                message.chat.id,
                audio=audio_file,
                title=info.get('title', 'Unknown'),
                performer=info.get('uploader', 'Unknown'),
                duration=duration,
                caption=(
                    f"🎵 {info.get('title')}\n"
                    f"👤 {info.get('uploader')}\n"
                    f"⏱ {duration//60}:{duration%60:02d}"
                )
            )
            await status_msg.delete()
        except Exception as send_error:
            await status_msg.edit_text(f"❌ Ошибка при отправке файла: {str(send_error)}")
        finally:
            # Очистка
            try:
                os.remove(audio_file)
                del search_results_cache[user_id]
            except:
                pass

    except Exception as e:
        error_message = str(e)
        if "ffmpeg" in error_message.lower():
            await message.reply(
                "❗️ Отсутствует FFmpeg!\n"
                "📝 Установите FFmpeg:\n"
                "- MacOS: brew install ffmpeg\n"
                "- Ubuntu: sudo apt-get install ffmpeg\n"
                "- Windows: скачайте с ffmpeg.org"
            )
        else:
            await message.reply(f"❗ Ошибка: {error_message}")

@app.on_message(filters.command("clear_downloads"))

# Function: async def clear_downloads_handler(client, message: Message):
# Description: Add a description here for the function's purpose.

async def clear_downloads_handler(client, message: Message):
    if message.from_user.id in allowed_user_ids:
        try:
            if os.path.exists('downloads'):
                for file in os.listdir('downloads'):
                    try:
                        os.remove(os.path.join('downloads', file))
                    except:
                        continue
                await message.reply("✅ Папка загрузок очищена!")
            else:
                await message.reply("📂 Папка загрузок пуста")
        except Exception as e:
            await message.reply(f"❗ Ошибка при очистке: {str(e)}")
    else:
        await message.reply("❌ У вас нет прав для использования этой команды!")


# -------------------------------------------------------------------------------------------------
# *** Работа с контекстом ***

# Функция для получения текущего времени в МСК

# Function: def get_time_in_msk():
# Description: Add a description here for the function's purpose.

def get_time_in_msk():
    return datetime.now(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")

# Загрузка контекста с использованием кэша

# Function: def load_context():
# Description: Add a description here for the function's purpose.

def load_context():
    global context_cache
    if not context_cache:
        if os.path.exists(context_file):
            with open(context_file, "r", encoding="utf-8") as f:
                context_cache = json.load(f)
        else:
            context_cache = {}
    return context_cache

# Сохранение контекста с обновлением кэша

# Function: def save_context(context):
# Description: Add a description here for the function's purpose.

def save_context(context):
    global context_cache
    context_cache = context
    with open(context_file, "w", encoding="utf-8") as f:
        json.dump(context, f, ensure_ascii=False, indent=4)

# Обновление контекста пользователя

# Function: def update_user_context(user_id, message):
# Description: Add a description here for the function's purpose.

def update_user_context(user_id, message):
    context = load_context()
    user_id_str = str(user_id)  # Преобразуем ID в строку для JSON
    if user_id_str not in context:
        context[user_id_str] = {"messages": [], "model": "gemini"}
    context[user_id_str]["messages"].append(message)
    if len(context[user_id_str]["messages"]) > 10:
        context[user_id_str]["messages"].pop(0)
    save_context(context)

# Получение текущей модели пользователя

# Function: def get_user_model(user_id):
# Description: Add a description here for the function's purpose.

def get_user_model(user_id):
    context = load_context()
    return context.get(str(user_id), {}).get("model", "gemini")

# -------------------------------------------------------------------------------------------------
# *** Работа с префиксом ***

# Загрузка префикса

# Function: def load_prefix():
# Description: Add a description here for the function's purpose.

def load_prefix():
    if os.path.exists(prefix_file):
        with open(prefix_file, "r", encoding="utf-8") as f:
            return json.load(f).get("prefix", "/")
    return "/"

# Сохранение префикса

# Function: def save_prefix(prefix):
# Description: Add a description here for the function's purpose.

def save_prefix(prefix):
    with open(prefix_file, "w", encoding="utf-8") as f:
        json.dump({"prefix": prefix}, f, ensure_ascii=False, indent=4)

# -------------------------------------------------------------------------------------------------
# *** Команды бота ***

@app.on_message(filters.command("help"))

# Function: async def help_handler(client, message: Message):
# Description: Add a description here for the function's purpose.

async def help_handler(client, message: Message):
    prefix = load_prefix()
    help_text = f"""
🤖 **Доступные команды:**

🔍 **Основные команды:**
{prefix}help - Показать это сообщение
{prefix}time - Показать время в разных городах мира
{prefix}info <user_id|username> - Информация о пользователе
{prefix}weather <город> - Узнать погоду в указанном городе

🎵 **Музыка:**
{prefix}music <название> - Поиск музыки
{prefix}download <номер> - Скачать песню по номеру из результатов поиска

🤖 **AI команды:**
{prefix}set_model <model_name> - Установка модели AI (g4f, gemini, chatgpt)
{prefix}gpt <текст> - Генерация ответа от AI
{prefix}clear_context - Очистить контекст пользователя

🎮 **Развлечения:**
{prefix}meme - Получить случайный мем


⚙️ **Настройки:**
{prefix}set_prefix <символ> - Установить новый префикс команд

💡 **Примеры использования:**
• {prefix}weather Москва
• {prefix}info @username
• {prefix}music In The End Linkin Park
"""

    await message.reply(help_text)

@app.on_message(filters.command("time"))

# Function: async def time_handler(client, message: Message):
# Description: Add a description here for the function's purpose.

async def time_handler(client, message: Message):
    # Dictionary of city timezones
    city_timezones = {
        "баку": "Asia/Baku",
        "москва": "Europe/Moscow",
        "лондон": "Europe/London",
        "париж": "Europe/Paris",
        "нью-йорк": "America/New_York",
        "токио": "Asia/Tokyo",
        "дубай": "Asia/Dubai",
        "стамбул": "Europe/Istanbul",
        "берлин": "Europe/Berlin",
        "рим": "Europe/Rome",
        "пекин": "Asia/Shanghai",
        "сеул": "Asia/Seoul",
        "сидней": "Australia/Sydney"
    }
    
    try:
        time_info = []
        for city, timezone in city_timezones.items():
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            time_info.append(f"🌍 {city.capitalize()}: {current_time.strftime('%H:%M:%S')}")
        
        # Join all times with newlines
        response = "⏰ Текущее время в городах:\n\n" + "\n".join(time_info)
        await message.reply(response)
    except Exception as e:
        await message.reply(f"❗ Ошибка при получении времени: {str(e)}")

@app.on_message(filters.command("info"))

# Function: async def info_handler(client, message: Message):
# Description: Add a description here for the function's purpose.

async def info_handler(client, message: Message):
    try:
        args = message.text.split(maxsplit=1)
        user_id = message.from_user.id

        if len(args) > 1:
            query = args[1]
            try:
                user_id = int(query)
            except ValueError:
                user = await client.get_users(query)
                user_id = user.id

        user = await client.get_users(user_id)
        chat_member = await client.get_chat_member(message.chat.id, user_id)

        # Сбор информации о пользователе
        language_code = user.language_code if user.language_code else 'Не указан'
        bio = getattr(user, 'bio', 'Нет биографии')
        status = chat_member.status
        joined_date = chat_member.joined_date.strftime('%Y-%m-%d %H:%M:%S') if chat_member.joined_date else 'Не указана'

        # Формируем текст с информацией
        info_text = f"""
👤 **Информация о пользователе:**

📌 **Основная информация:**
• ID: `{user.id}`
• Имя: {user.first_name}
• Фамилия: {user.last_name or 'Не указана'}
• Username: @{user.username or 'Не указан'}

🌍 **Дополнительно:**
• Язык: {language_code}
• Бот: {'Да' if user.is_bot else 'Нет'}
• Биография: {bio}

📊 **Статус в чате:**
• Роль: {status}
• Администратор: {'Да' if status == 'administrator' else 'Нет'}
• Владелец: {'Да' if status == 'creator' else 'Нет'}
• Участник: {'Да' if status == 'member' else 'Нет'}

📅 **Даты:**
• Дата вступления: {joined_date}
"""
        try:
            created_at = user.date.strftime('%Y-%m-%d %H:%M:%S') if user.date else 'Не указана'
            info_text += f"• Дата регистрации: {created_at}"
        except AttributeError:
            info_text += "• Дата регистрации: Не указана"

        await message.reply(info_text)

    except Exception as e:
        await message.reply(f"❗ Ошибка при получении информации: {str(e)}")

@app.on_message(filters.command("set_model"))

# Function: async def set_model_handler(client, message: Message):
# Description: Add a description here for the function's purpose.

async def set_model_handler(client, message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.reply(f"❗ Укажите модель: {', '.join(AVAILABLE_MODELS)}")
        return
    
    model = args[1].lower()
    if model not in AVAILABLE_MODELS:
        await message.reply(f"❗ Неверная модель. Доступные модели: {', '.join(AVAILABLE_MODELS)}")
        return
    
    context = load_context()
    user_id = str(message.from_user.id)
    if user_id not in context:
        context[user_id] = {"messages": []}
    context[user_id]["model"] = model
    save_context(context)
    await message.reply(f"✅ Модель установлена: {model}")

@app.on_message(filters.command("clear_context"))

# Function: async def clear_context_handler(client, message: Message):
# Description: Add a description here for the function's purpose.

async def clear_context_handler(client, message: Message):
    try:
        user_id = str(message.from_user.id)
        context = load_context()
        
        if user_id in context:
            del context[user_id]
            save_context(context)
            await message.reply("✅ Контекст пользователя успешно очищен")
        else:
            await message.reply("ℹ️ У вас нет сохраненного контекста")
    except Exception as e:
        await message.reply(f"❗ Ошибка при очистке контекста: {str(e)}")

@app.on_message(filters.command("set_prefix"))

# Function: async def set_prefix_handler(client, message: Message):
# Description: Add a description here for the function's purpose.

async def set_prefix_handler(client, message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.reply("❗ Укажите новый префикс. Пример: /set_prefix !")
        return
    
    new_prefix = args[1]
    if len(new_prefix) != 1:
        await message.reply("❗ Префикс должен быть одним символом")
        return
    
    save_prefix(new_prefix)
    await message.reply(f"✅ Установлен новый префикс: {new_prefix}")

# -------------------------------------------------------------------------------------------------
# *** Спам-атаки ***

# Спам-атака
@app.on_message(filters.command("spamattack"))

# Function: async def spamattack(client, message: Message):
# Description: Add a description here for the function's purpose.

async def spamattack(client, message: Message):
    global stop_spam_flag
    if message.from_user.id not in allowed_user_ids:
        await message.reply("❗ У вас нет прав для использования этой команды.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❗ Укажите количество сообщений, например: /spamattack 5")
        return

    try:
        count = int(args[1].strip())
        if count <= 0:
            await message.reply("❗ Количество сообщений должно быть больше нуля.")
            return

        stop_spam_flag = False
        await message.reply(f"Начинаю спамить {count} сообщений!")

        for i in range(count):
            if stop_spam_flag:
                await message.reply("⚠️ Спам остановлен.")
                return
            await client.send_sticker(message.chat.id, STICKER_ID)
        await message.reply("✅ Спам завершён!")
    except ValueError:
        await message.reply("❗ Укажите корректное число.")

# Остановка спама
@app.on_message(filters.command("stopspam"))

# Function: async def stopspam(client, message: Message):
# Description: Add a description here for the function's purpose.

async def stopspam(client, message: Message):
    global stop_spam_flag
    if message.from_user.id not in allowed_user_ids:
        await message.reply("❗ У вас нет прав для использования этой команды.")
        return
    stop_spam_flag = True
    await message.reply("⛔ Спам будет остановлен.")

# -------------------------------------------------------------------------------------------------
# *** Генерация ответа ИИ ***

# Генерация ответа от ИИ

# Function: async def get_ai_response(model, message, user_id):
# Description: Add a description here for the function's purpose.

async def get_ai_response(model, message, user_id):
    try:
        context = load_context()
        user_context = context.get(str(user_id), {}).get("messages", [])
        full_message = "\n".join(user_context) + f"\n{message}"
        
        if model == "g4f":
            return await asyncio.to_thread(g4f_response, full_message)
        elif model == "gemini":
            return await asyncio.to_thread(gemini_response, full_message)
        elif model == "chatgpt":
            return await asyncio.to_thread(chatgpt_response, full_message)
        return "Неизвестная модель."
    except Exception as e:
        print(f"Ошибка в get_ai_response: {e}")
        return "Произошла ошибка при генерации ответа."

# -------------------------------------------------------------------------------------------------
# *** Получение мемов ***

MEME_API_URL = "https://meme-api.com/gimme"

@app.on_message(filters.command("meme"))

# Function: async def meme_handler(client, message: Message):
# Description: Add a description here for the function's purpose.

async def meme_handler(client, message: Message):
    try:
        response = requests.get(MEME_API_URL)
        data = response.json()

        # Проверяем, что URL мемов существует
        if data.get("url"):
            await message.reply_photo(data["url"])
        else:
            await message.reply("❗ Не удалось загрузить мем. Попробуйте позже.")
    except Exception as e:
        await message.reply(f"❗ Ошибка при получении мема: {str(e)}")



# -------------------------------------------------------------------------------------------------
# *** Погода ***

"""
Как использовать:
1. Получить API ключи:
   - OpenWeatherMap API (https://openweathermap.org/api)
   - Telegram API (https://my.telegram.org/apps)
2. Заполнить config.py своими ключами

Формат вывода погоды:
🌡 ПОГОДА НА СЕГОДНЯ (Город)
⛅️ Текущая погода
↖️ Ветер и влажность
🌤 Прогноз на сегодня
☀️ Прогноз на завтра
☁️ Прогноз на послезавтра
"""

@app.on_message(filters.command("weather"))

# Function: async def weather_handler(client, message: Message):
# Description: Add a description here for the function's purpose.

async def weather_handler(client, message: Message):
    """
    Обработчик команды /weather
    Использование: /weather Город
    Пример: /weather Баку
    """
    # Проверка наличия названия города
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "❗ Укажите город\n"
            "Пример: /weather Баку\n"
            "🌍 Поддерживаются города по всему миру"
        )
        return

    city = args[1].strip()
    
    # URL endpoints для API запросов
    BASE_URL = "http://api.openweathermap.org/data/2.5"
    GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
    
    # Общие параметры для всех запросов
    base_params = {
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    try:
        # 1. Получаем координаты города
        geo_response = requests.get(GEO_URL, params={
            **base_params,
            "q": city,
            "limit": 1
        })
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data:
            await message.reply(
                "❗ Город не найден\n"
                "Проверьте правильность написания города\n"
                "Пример: /weather Баку"
            )
            return

        lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]

        # 2. Получаем текущую погоду
        current_response = requests.get(f"{BASE_URL}/weather", params={
            **base_params,
            "lat": lat,
            "lon": lon
        })
        current_response.raise_for_status()
        current = current_response.json()

        # 3. Получаем прогноз погоды
        forecast_response = requests.get(f"{BASE_URL}/forecast", params={
            **base_params,
            "lat": lat,
            "lon": lon
        })
        forecast_response.raise_for_status()
        forecast = forecast_response.json()

        # Форматируем текущую погоду
        current_temp = round(current["main"]["temp"])
        current_desc = current["weather"][0]["description"]
        wind_speed = current["wind"]["speed"]
        wind_deg = current["wind"]["deg"]
        humidity = current["main"]["humidity"]

        # Определяем направление ветра

# Function: def get_wind_direction(degrees):
# Description: Add a description here for the function's purpose.

        def get_wind_direction(degrees):
            directions = ["↑", "↗️", "→", "↘️", "↓", "↙️", "←", "↖️"]
            index = round(degrees / 45) % 8
            return directions[index]

        wind_direction = get_wind_direction(wind_deg)

        # Структурируем прогноз по дням и времени суток
        forecasts = {}
        for item in forecast["list"]:
            dt = datetime.fromtimestamp(item["dt"])
            date = dt.strftime("%Y-%m-%d")
            hour = dt.hour
            
            if date not in forecasts:
                forecasts[date] = {
                    "night": [], # 00-06
                    "morning": [], # 06-12
                    "day": [], # 12-18
                    "evening": [] # 18-00
                }
            
            temp = round(item["main"]["temp"])
            desc = item["weather"][0]["description"]
            
            if 0 <= hour < 6:
                forecasts[date]["night"].append((temp, desc))
            elif 6 <= hour < 12:
                forecasts[date]["morning"].append((temp, desc))
            elif 12 <= hour < 18:
                forecasts[date]["day"].append((temp, desc))
            else:
                forecasts[date]["evening"].append((temp, desc))

        # Формируем сообщение
        message_text = f"🌡 ПОГОДА НА СЕГОДНЯ ({city})\n"
        message_text += f"⛅️ Сейчас: +{current_temp}° {current_desc}\n"
        message_text += f"Ветер: {wind_direction} {wind_speed:.2f} м/с, влажность: {humidity}%\n\n"

        # Добавляем прогноз по дням
        dates = list(forecasts.keys())
        
        # Сегодня
        if dates:
            today = dates[0]
            today_data = forecasts[today]
            if today_data["evening"]:
                temp, desc = today_data["evening"][0]
                message_text += f"Cегодня\n🌤 Вечером: +{temp}..+{temp}°, {desc}\n\n"

        # Завтра
        if len(dates) > 1:
            tomorrow = dates[1]
            tomorrow_data = forecasts[tomorrow]
            message_text += "Завтра\n"
            
            for period, emoji in [
                ("night", "🌤"),
                ("morning", "☀️"),
                ("day", "☀️"),
                ("evening", "⛅️")
            ]:
                if tomorrow_data[period]:
                    temp, desc = tomorrow_data[period][0]
                    period_name = {
                        "night": "Ночью",
                        "morning": "Утром",
                        "day": "Днём",
                        "evening": "Вечером"
                    }[period]
                    message_text += f"{emoji} {period_name}: +{temp}..+{temp}°, {desc}\n"
            message_text += "\n"

        # Послезавтра
        if len(dates) > 2:
            day_after = dates[2]
            after_data = forecasts[day_after]
            next_date = datetime.strptime(day_after, "%Y-%m-%d").strftime("%d.%m.%Y")
            message_text += f"{next_date}\n"
            
            for period, emoji in [
                ("night", "☁️"),
                ("morning", "⛅️"),
                ("day", "☁️")
            ]:
                if after_data[period]:
                    temp, desc = after_data[period][0]
                    period_name = {
                        "night": "Ночью",
                        "morning": "Утром",
                        "day": "Днём"
                    }[period]
                    message_text += f"{emoji} {period_name}: +{temp}..+{temp}°, {desc}\n"

        await message.reply(message_text)

    except requests.exceptions.RequestException as e:
        error_message = (
            "❗ Ошибка при запросе погоды\n"
            f"Причина: {str(e)}\n"
            "Попробуйте позже или проверьте название города"
        )
        await message.reply(error_message)
    except Exception as e:
        error_message = (
            "❗ Непредвиденная ошибка\n"
            f"Причина: {str(e)}\n"
            "Пожалуйста, сообщите об ошибке разработчику"
        )
        await message.reply(error_message)





# Запуск клиента
if __name__ == "__main__":
    print("Бот запущен. V0.2.0. By Mikayilaz")
    app.run()
