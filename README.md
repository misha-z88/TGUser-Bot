***Команды***


**Команда**	  ***< значание >***   -      **Описание**
```
/help - Справка.
/time - Текущее время в МСК.
/info - Информация о пользователе.
/set_model <model_name> - Установка модели (g4f, gemini, chatgpt).
/gpt <текст> - Генерация ответа.
/set_prefix <символ> - Установить новый префикс.
/weather <город> - Узнать погоду в указанном городе.
/clear_context - Очистить контекст пользователя.
```

Вы можете обновить префикс команды бота, используя /set_prefix <new_prefix>. По умолчанию, ***/.***

***ИИ*** 🪄

Бот поддерживает:

[Gemini](https://gemini.google.com/?hl=ru) (ИИ от Google) : Хороший

[G4F](https://github.com/techwithanirudh/g4f) (model = gpt-3.5-turbo ) : Не требует API

[ChatGPT](https://chatgpt.com/) (model = gpt-3.5-turbo ) : Надежный

 

Установите модель с помощью  ``/set_model <model_name>.``
    
Перед запуском напишите ``pip install -r requirements txt``

Еще одна команда которую вы можете добавить для спама в ЛС и в Чаты стикерами

*❗️* ***ВЫ МОЖЕТЕ ПОЛУЧИТЬ БАН ЗА СПАМ В ТЕЛЕГРАММЕ*** *❗️* 


```

# Список авторизованных пользователей
allowed_user_ids = [2161024343, 2244396277]  # Замените на ID пользователей, которым разрешено использовать команды

# Флаг для остановки спама
stop_spam_flag = False

@app.on_message(filters.command("spamattack"))
async def spamattack(client, message):
    global stop_spam_flag

    # Проверяем, есть ли отправитель в списке разрешённых пользователей
    if message.from_user.id not in allowed_user_ids:
        await message.reply("❗ У вас нет прав для использования этой команды.")
        return

    # Разделяем команду и аргумент
    args = message.text.split(maxsplit=1)

    # Если аргумент не указан
    if len(args) < 2:
        await message.reply("❗ Укажите количество сообщений, например: /spamattack 5")
        return

    try:
        # Пробуем преобразовать аргумент в число
        count = int(args[1].strip())

        if count <= 0:
            await message.reply("❗ Количество сообщений должно быть больше нуля.")
            return

        # Сбрасываем флаг перед началом спама
        stop_spam_flag = False

        await message.reply(f"Начинаю спамить {count} сообщений!")

        # Цикл отправки сообщений
        for i in range(count):
            if stop_spam_flag:
                await message.reply("⚠️ Спам остановлен.")
                return

            await client.send_sticker(message.chat.id, STICKER_ID)  # Укажите ваш ID стикера
            await asyncio.sleep(1)  # Пауза между сообщениями

        await message.reply("✅ Спам завершён!")
    except ValueError:
        await message.reply("❗ Укажите корректное число, например: /spamattack 5")

@app.on_message(filters.command("stopspam"))
async def stopspam(client, message):
    global stop_spam_flag

    # Проверяем, есть ли отправитель в списке разрешённых пользователей
    if message.from_user.id not in allowed_user_ids:
        await message.reply("❗ У вас нет прав для использования этой команды.")
        return

    # Устанавливаем флаг для остановки
    stop_spam_flag = True
    await message.reply("⛔ Спам будет остановлен.")


```

*❗️* ***ВЫ МОЖЕТЕ ПОЛУЧИТЬ ТАКУЮ ОШИБКУ ВО ВРЕМЯ ИСПОЛЬЗОВАНИЯ API GEMINI ИЗ-ЗА КАТЕГОРИИ ВОПРОСА СЕКСУАЛЬНОГО и/или НЕЗАКОННОГО ХАРАКТЕРА*** *❗️* 

```
Oшибка при использовании Gemini: ("Invalid operation: The response.text quick accessor requires the response to contain a valid Part, but none were returned. The candidate's [finish_reason](https://ai.google.dev/api/generate-content#finishreason) is 3. The candidate's safety_ratings are: [category: HARM_CATEGORY_SEXUALLY_EXPLICIT\nprobability: HIGH\n, category: HARM_CATEGORY_HATE_SPEECH\nprobability: NEGLIGIBLE\n, category: HARM_CATEGORY_HARASSMENT\nprobability: NEGLIGIBLE\n, category: HARM_CATEGORY_DANGEROUS_CONTENT\nprobability: NEGLIGIBLE\n].", [category: HARM_CATEGORY_SEXUALLY_EXPLICIT
probability: HIGH
, category: HARM_CATEGORY_HATE_SPEECH
probability: NEGLIGIBLE
, category: HARM_CATEGORY_HARASSMENT
probability: NEGLIGIBLE
, category: HARM_CATEGORY_DANGEROUS_CONTENT
probability: NEGLIGIBLE
])
```
*Ошибка, которую вы получили, связана с системой безопасности API Gemini (Google Generative AI). Она блокирует ответы, если они содержат или могут быть интерпретированы как опасные или запрещенные темы. В данном случае проблема связана с категорией "сексуально-эксплицитный контент" (HARM_CATEGORY_SEXUALLY_EXPLICIT) с высокой вероятностью.*




Бот при первом запуске попросит BOT TOKEN или же ваш номер телефона для входа в аккаунт и введите код потверждения для! Если вы зашли в аккаунт и хотете поменять аккаунт, то удалите файлы mybot.session (все файлы с этим названием) 

***[Поддержать автора](https://www.donationalerts.com/r/adolmi)***
