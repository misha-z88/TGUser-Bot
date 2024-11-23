from g4f import Provider, ChatCompletion, models
import google.generativeai as genai
import openai
import traceback

# Инициализация пользовательских настроек
user_choise = {}

# Инициализация Gemini API 
genai.configure(api_key='') #API GEMINI!
model = genai.GenerativeModel("gemini-1.5-flash")

# Инициализация OpenAI API
client_openai = openai.OpenAI( #API META!
    api_key="",
    base_url="https://api.sambanova.ai/v1/chat/completions",
)

def g4f_response(text) -> str:
    """Обработка запроса через g4f"""
    try:
        print(f"[G4F] Получен запрос: {text}")
        gpt_reply = ChatCompletion.create(
            model='gpt-35-turbo',
            provider=Provider.TeachAnything,
            messages=[{"role": "user", "content": text}]
        )
        if gpt_reply:
            print(f"[G4F] Ответ: {gpt_reply}")
            return gpt_reply
        else:
            return "G4F не смог сгенерировать ответ."
    except Exception as e:
        print(f"[G4F] Ошибка: {e}")
        print(traceback.format_exc())
        return f"Ошибка G4F: {e}"

def meta_response(text) -> str:
    """Обработка запроса через Meta API"""
    try:
        print(f"[Meta] Получен запрос: {text}")
        response = client_openai.chat.completions.create(
            model='Meta-Llama-3.1-8B-Instruct',
            messages=[{"role": "user", "content": text}],
            temperature=0.1,
            top_p=0.1
        )
        meta_reply = response.choices[0].message.content if response and response.choices else None
        if meta_reply:
            print(f"[Meta] Ответ: {meta_reply}")
            return meta_reply
        else:
            return "Meta не смог сгенерировать ответ."
    except Exception as e:
        print(f"[Meta] Ошибка: {e}")
        print(traceback.format_exc())
        return f"Ошибка Meta: {e}"

def gemini_response(text):
    """Обработка запроса через Gemini API"""
    try:
        print(f"[Gemini] Получен запрос: {text}")
        response = model.generate_content(text)
        if hasattr(response, 'text') and response.text:
            print(f"[Gemini] Ответ: {response.text}")
            return response.text
        else:
            return "Gemini не смог сгенерировать ответ."
    except Exception as e:
        print(f"[Gemini] Ошибка: {e}")
        print(traceback.format_exc())
        return f"Ошибка при генерации ответа: {e}"

def with_reply(func):
    """Декоратор для проверки, что команда является ответом на сообщение"""
    async def wrapped(client, message):
        if not message.reply_to_message:
            await message.reply("<b>Reply to message is required</b>")
            return  # Останавливаем выполнение, если условия не выполнены
        return await func(client, message)
    return wrapped
