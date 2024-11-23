***Команды***


**Команда**	  ***< значание >***   -      **Описание**
```
/help	- Справка.
/info	- Информация о пользователе который ввел команду.
/time	- Показывает текущее время в МСК 0.
/weather < город > - Узнать погоду в <город>.
/set_prefix < символ > - Изменить префикс на < символ > (По умолчанию " / ")
/set_model < model > - Устанавливает модель ИИ (gemini, g4f, meta).
/gpt < text > - Спросить у ИИ (< model >) вопрос.
/clear_context - Очистить контекст пользователя

Вместо </> будет префикс который вы установили!
```

Вы можете обновить префикс команды бота, используя /set_prefix <new_prefix>. По умолчанию, ***/.***

***ИИ***

Бот поддерживает:

[Gemini](https://gemini.google.com/?hl=ru) (ИИ от Google) : Хороший

[G4F](https://github.com/techwithanirudh/g4f) (model = gpt-3.5-turbo ) : Не требует API

[ChatGPT](https://chatgpt.com/) (model = gpt-3.5-turbo ) : Надежный

 

Установите модель с помощью  ```/set_model <model_name>.```
    
Перед запуском напишите ```pip install -r requirements txt```

Еще одна команда которут вы можете добавить для спама в ЛС и в Чаты стикерами

*❗️* ***ВЫ МОЖЕТЕ ПОЛУЧИТЬ БАН ЗА СПАМ В ТЕЛЕГРАММЕ*** *❗️* 


```
# Задаём ID пользователя и ID стикера
TARGET_ID =  TG_ID        # Введите ваш ID пользователя или же несколько ID использую []
STICKER_ID = "STICKER_ID   "      # Введите ID Стикера которым будет спамить бот (Что бы узнать ID стикера, скиньте стикер ID которого вы хотите узнать боту @idstickerbot)

@app.on_message(filters.command("spamattack") & filters.private | filters.group)
async def spamattack(client, message):
    # Проверка ID отправителя
    if message.from_user.id == TARGET_ID:
        # Спрашиваем количество сообщений
        ask_message = await message.reply("Сколько сообщений нужно отправить? Введите число:")
        
        # Ожидание ответа
        try:
            response = await client.listen(message.chat.id, timeout=30)  # Ждём ответ 30 секунд
            count = int(response.text)
            
            if count <= 0:
                await message.reply("Количество сообщений должно быть больше нуля.")
                return
            
            # Удаляем запрос, если это уместно
            await ask_message.delete()
            await response.delete()

            await message.reply(f"Начинаю спамить {count} сообщений!")
            
            # Цикл отправки стикеров
            for _ in range(count):
                await client.send_sticker(message.chat.id, STICKER_ID)
                await asyncio.sleep(1)  # Пауза между сообщениями

            await message.reply("Спам завершён!")
        except asyncio.TimeoutError:
            await message.reply("Вы не ответили в течение 30 секунд. Команда отменена.")
        except ValueError:
            await message.reply("Нужно ввести число. Попробуйте ещё раз.")
    else:
        await message.reply("У вас нет прав для использования этой команды.")

# Запуск приложения
app.run()

```


Бот при первом запуске попросит BOT TOKEN или же ваш номер телефона для входа в аккаунт и введите код потверждения для! Если вы зашли в аккаунт и хотете поменять аккаунт, то удалите файлы mybot.session (все файлы с этим названием) 

***[Поддержать автора](https://www.donationalerts.com/r/adolmi)***
