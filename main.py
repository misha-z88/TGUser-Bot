"""
╔══════════════════════════════════════╗
║                                      ║
║            USER BOT v0.3.0           ║
║                                      ║
║         Created by @misha_z88        ║
║                                      ║
╚══════════════════════════════════════╝

GitHub: https://github.com/misha-z88
"""

import json
import os
import pytz
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import asyncio
from config import API_ID, API_HASH, WEATHER_API_KEY
from google.generativeai import GenerativeModel, configure
from config import GOOGLE_API_KEY
import PIL.Image
from io import BytesIO
import wikipedia
import qrcode

configure(api_key=GOOGLE_API_KEY)
model = GenerativeModel('gemini-pro')
vision_model = GenerativeModel('gemini-pro-vision')

app = Client("mybot", api_id=API_ID, api_hash=API_HASH)

context_file = "context.json"
prefix_file = "prefix.json"
context_cache = {}
WEATHER_URL = "https://api.openweathermap.org/data/2.5/onecall"

def load_context():
    global context_cache
    if not context_cache:
        if os.path.exists(context_file):
            with open(context_file, "r", encoding="utf-8") as f:
                context_cache = json.load(f)
        else:
            context_cache = {}
    return context_cache

def save_context(context):
    global context_cache
    context_cache = context
    with open(context_file, "w", encoding="utf-8") as f:
        json.dump(context, f, ensure_ascii=False, indent=4)

def update_user_context(user_id, role, message):
    context = load_context()
    user_id_str = str(user_id)
    if user_id_str not in context:
        context[user_id_str] = []
    context[user_id_str].append({"role": role, "content": message})
    if len(context[user_id_str]) > 10:
        context[user_id_str].pop(0)
    save_context(context)

def load_prefix():
    if os.path.exists(prefix_file):
        with open(prefix_file, "r", encoding="utf-8") as f:
            return json.load(f).get("prefix", "/")
    return "/"

def save_prefix(prefix):
    with open(prefix_file, "w", encoding="utf-8") as f:
        json.dump({"prefix": prefix}, f, ensure_ascii=False, indent=4)

def format_message(title, content):
    return f"""
╭─「 {title} 」
│
{content.replace('\\n', '\\n│ ')}
│
╰────────────"""

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    prefix = load_prefix()
    welcome_text = format_message("Добро пожаловать!", f"""
Я - многофункциональный User-бот с AI!

🤖 Основные возможности:
• Интеграция с Google Gemini Pro
• Анализ изображений
• Помощь с домашними заданиями
• Погода, время и многое другое

📝 Используйте {prefix}help для просмотра всех команд

👨‍💻 GitHub: https://github.com/misha-z88
📢 Telegram: @misha_z88
""")
    await message.reply(welcome_text)

@app.on_message(filters.command("help"))
async def help_handler(client, message: Message):
    prefix = load_prefix()
    help_text = format_message("Доступные команды", f"""
🔍 Основные команды:
• {prefix}help - Это сообщение
• {prefix}time - Мировое время
• {prefix}info - Информация о пользователе
• {prefix}weather - Погода в городе

🤖 AI команды:
• {prefix}ai - Запрос к Gemini AI
• {prefix}image - Анализ изображения
• {prefix}homework - Помощь с заданиями
• {prefix}clear_context - Очистка контекста

🛠 Инструменты:
• {prefix}qr - Создать QR-код
• {prefix}wiki - Поиск в Wikipedia
• {prefix}translate - Перевод текста
• {prefix}calc - Калькулятор
• {prefix}chat_info - Информация о чате
• {prefix}get_users - Список пользователей
• {prefix}purge - Удаление сообщений
• {prefix}download - Скачать медиа

🎮 Развлечения:
• {prefix}meme - Случайный мем
• {prefix}poll - Создать опрос

⚙️ Настройки:
• {prefix}set_prefix - Изменить префикс

💡 Примеры:
• {prefix}weather Москва
• {prefix}ai Расскажи о квантовой физике
• {prefix}homework Реши уравнение: 2x + 5 = 15""")

    await message.reply(help_text)

@app.on_message(filters.command("weather"))
async def weather_handler(client, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply(
                format_message("Ошибка",
                    "❗ Укажите город\n"
                    "Пример: /weather Москва"
                )
            )
            return

        city = message.command[1]
        
        geo_response = requests.get(
            "http://api.openweathermap.org/geo/1.0/direct",
            params={
                "q": city,
                "limit": 1,
                "appid": WEATHER_API_KEY
            }
        )
        geo_data = geo_response.json()

        if not geo_data:
            await message.reply(
                format_message("Ошибка",
                    "❗ Город не найден\n"
                    "Проверьте правильность написания"
                )
            )
            return

        lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
        
        weather_response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": lat,
                "lon": lon,
                "appid": WEATHER_API_KEY,
                "units": "metric",
                "lang": "ru"
            }
        )
        weather_data = weather_response.json()

        temp = round(weather_data["main"]["temp"])
        feels_like = round(weather_data["main"]["feels_like"])
        description = weather_data["weather"][0]["description"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]
        
        weather_text = format_message(f"Погода в {city}", f"""
🌡 Температура: {temp}°C
🌡 Ощущается как: {feels_like}°C
☁️ {description.capitalize()}
💧 Влажность: {humidity}%
💨 Ветер: {wind_speed} м/с""")

        await message.reply(weather_text)

    except Exception as e:
        await message.reply(
            format_message("Ошибка",
                f"❗ Произошла ошибка: {str(e)}"
            )
        )

@app.on_message(filters.command("qr"))
async def qr_handler(client, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply("❗ Использование: /qr текст")
            return

        text = " ".join(message.command[1:])
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        bio = BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        
        await message.reply_photo(
            bio,
            caption=format_message("QR Code", f"Создан для: {text[:50]}...")
        )
    except Exception as e:
        await message.reply(f"❗ Ошибка: {str(e)}")

@app.on_message(filters.command("wiki"))
async def wiki_handler(client, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply("❗ Использование: /wiki запрос")
            return

        query = " ".join(message.command[1:])
        wikipedia.set_lang("ru")
        result = wikipedia.summary(query, sentences=5)
        
        await message.reply(
            format_message("Wikipedia", f"🔍 Запрос: {query}\n\n{result}")
        )
    except Exception as e:
        await message.reply(f"❗ Ошибка: {str(e)}")

@app.on_message(filters.command("poll"))
async def poll_handler(client, message: Message):
    try:
        args = message.text.split("\n")
        if len(args) < 3:
            await message.reply(
                "❗ Использование:\n/poll Вопрос\nВариант 1\nВариант 2\n..."
            )
            return

        question = args[0].replace("/poll ", "")
        options = args[1:]
        
        await message.reply_poll(
            question,
            options,
            is_anonymous=False
        )
    except Exception as e:
        await message.reply(f"❗ Ошибка: {str(e)}")

@app.on_message(filters.command("time"))
async def time_handler(client, message: Message):
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
        
        response = format_message("Мировое время", "\n".join(time_info))
        await message.reply(response)
    except Exception as e:
        await message.reply(f"❗ Ошибка при получении времени: {str(e)}")

@app.on_message(filters.command("ai"))
async def ai_handler(client, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply("❗ Использование: /ai <ваш запрос>")
            return

        user_query = " ".join(message.command[1:])
        user_id = str(message.from_user.id)
        
        context = load_context()
        user_context = context.get(user_id, [])
        
        messages = []
        for msg in user_context:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_query})
        
        response = model.generate_content(user_query)
        ai_response = response.text
        
        update_user_context(user_id, "user", user_query)
        update_user_context(user_id, "assistant", ai_response)
        
        await message.reply(ai_response)
        
    except Exception as e:
        await message.reply(f"❗ Ошибка при обработке запроса: {str(e)}")

@app.on_message(filters.command("image") & filters.photo)
async def image_handler(client, message: Message):
    try:
        if not message.caption:
            await message.reply("❗ Добавьте описание к изображению")
            return

        photo = message.photo.file_id
        file_path = await client.download_media(photo)
        
        img = PIL.Image.open(file_path)
        response = vision_model.generate_content([message.caption, img])
        
        os.remove(file_path)
        await message.reply(response.text)
        
    except Exception as e:
        await message.reply(f"❗ Ошибка при обработке изображения: {str(e)}")

@app.on_message(filters.command("homework"))
async def homework_handler(client, message: Message):
    try:
        if message.photo:
            if not message.caption:
                await message.reply("❗ Добавьте описание задачи к фотографии")
                return
                
            photo = message.photo.file_id
            file_path = await client.download_media(photo)
            
            img = PIL.Image.open(file_path)
            response = vision_model.generate_content([
                "Помоги решить эту задачу. Объясни решение подробно, шаг за шагом: " + message.caption,
                img
            ])
            
            os.remove(file_path)
            await message.reply(response.text)
            
        elif len(message.command) > 1:
            query = " ".join(message.command[1:])
            response = model.generate_content(
                "Помоги решить эту задачу. Объясни решение подробно, шаг за шагом: " + query
            )
            await message.reply(response.text)
            
        else:
            await message.reply("❗ Отправьте фото задачи с описанием или текст задачи")
            
    except Exception as e:
        await message.reply(f"❗ Ошибка при обработке запроса: {str(e)}")

@app.on_message(filters.command("clear_context"))
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

@app.on_message(filters.command("chat_info"))
async def chat_info_handler(client, message: Message):
    try:
        if len(message.command) < 2:
            chat = message.chat
        else:
            chat_username = message.command[1].replace("@", "")
            chat = await client.get_chat(chat_username)
        
        info = format_message("Информация о чате", f"""
📊 Основная информация:
• ID: {chat.id}
• Тип: {chat.type}
• Название: {chat.title if chat.title else 'Н/Д'}
• Юзернейм: {chat.username if chat.username else 'Н/Д'}
• Описание: {chat.description if chat.description else 'Н/Д'}
• Количество участников: {chat.members_count if hasattr(chat, 'members_count') else 'Н/Д'}
• Создан: {chat.date if hasattr(chat, 'date') else 'Н/Д'}
""")
        await message.reply(info)
    except Exception as e:
        await message.reply(f"❗ Ошибка: {str(e)}")

@app.on_message(filters.command("purge"))
async def purge_handler(client, message: Message):
    try:
        if len(message.command) != 2:
            await message.reply("❗ Использование: /purge количество_сообщений")
            return
            
        count = int(message.command[1])
        if count > 1000:
            await message.reply("❗ Максимальное количество сообщений для удаления: 1000")
            return
            
        messages_to_delete = []
        async for msg in client.get_chat_history(message.chat.id, limit=count):
            if msg.from_user and msg.from_user.id == client.me.id:
                messages_to_delete.append(msg.id)
                
        await client.delete_messages(message.chat.id, messages_to_delete)
        status_msg = await message.reply(f"✅ Удалено {len(messages_to_delete)} сообщений")
        await asyncio.sleep(3)
        await status_msg.delete()
        
    except Exception as e:
        await message.reply(f"❗ Ошибка: {str(e)}")

@app.on_message(filters.command("get_users"))
async def get_users_handler(client, message: Message):
    try:
        if not message.chat.id:
            await message.reply("❗ Эта команда работает только в чатах")
            return
            
        users_info = []
        async for member in client.get_chat_members(message.chat.id):
            user = member.user
            users_info.append(f"• {user.first_name} ({user.id})")
            if len(users_info) >= 20: 
                break
                
        response = format_message("Пользователи чата", "\n".join(users_info))
        await message.reply(response)
        
    except Exception as e:
        await message.reply(f"❗ Ошибка: {str(e)}")

@app.on_message(filters.command("download"))
async def download_handler(client, message: Message):
    try:
        if not message.reply_to_message:
            await message.reply("❗ Ответьте на сообщение с медиафайлом")
            return
            
        reply = message.reply_to_message
        
        if reply.photo:
            path = await client.download_media(reply.photo.file_id)
            media_type = "фото"
        elif reply.video:
            path = await client.download_media(reply.video.file_id)
            media_type = "видео"
        elif reply.document:
            path = await client.download_media(reply.document.file_id)
            media_type = "файл"
        elif reply.audio:
            path = await client.download_media(reply.audio.file_id)
            media_type = "аудио"
        else:
            await message.reply("❗ Неподдерживаемый тип медиафайла")
            return
            
        await message.reply(
            format_message("Загрузка завершена", 
                f"✅ {media_type.capitalize()} сохранен в: {path}"
            )
        )
        
    except Exception as e:
        await message.reply(f"❗ Ошибка: {str(e)}")

@app.on_message(filters.command("set_prefix"))
async def set_prefix_handler(client, message: Message):
    try:
        if len(message.command) != 2:
            await message.reply(
                format_message("Ошибка",
                    "❗ Укажите новый префикс. Пример: /set_prefix !"
                )
            )
            return
        
        new_prefix = message.command[1]
        if len(new_prefix) != 1:
            await message.reply(
                format_message("Ошибка",
                    "❗ Префикс должен быть одним символом"
                )
            )
            return
        
        save_prefix(new_prefix)
        await message.reply(
            format_message("Успех",
                f"✅ Установлен новый префикс: {new_prefix}"
            )
        )
    except Exception as e:
        await message.reply(f"❗ Ошибка: {str(e)}")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════╗
║                                      ║
║         USER BOT v0.3.0              ║
║         Starting...                  ║
║                                      ║
║         by @misha_z88                ║
║                                      ║
╚══════════════════════════════════════╝
    """)
    app.run()
