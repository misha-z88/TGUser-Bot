import g4f
import openai
import google.generativeai as genai
from config import GEMINI_API_KEY, OPENAI_API_KEY

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

# Настройка OpenAI
openai.api_key = OPENAI_API_KEY

def gemini_response(prompt):
    try:
        # Генерация ответа с помощью Gemini
        print("Запрос к Gemini...")
        response = gemini_model.generate_content(prompt)
        print("Ответ от Gemini:", response.text)
        return response.text
    except Exception as e:
        # Логирование ошибки и возврат сообщения
        print(f"Ошибка при использовании Gemini: {e}")
        return "Произошла ошибка при генерации ответа с использованием Gemini."

def g4f_response(prompt):
    try:
        print("Запрос к g4f...")
        # Выбор провайдера g4f
        response = g4f.ChatCompletion.create(
            model="gpt-4-turbo",  # Используем модель GPT-4-Turbo
            provider=g4f.Provider.Liaobots,  # Используем провайдера Liaobots
            messages=[{"role": "user", "content": prompt}],
        )

        # Печать ответа от g4f для отладки
        print(f"Ответ от g4f: {response}")

        # Если ответ от g4f это строка, возвращаем его напрямую
        if isinstance(response, str):
            return response

        # Если ответ имеет ожидаемую структуру, обрабатываем его
        if isinstance(response, dict):
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['message']['content']
            else:
                print("Ответ от g4f не содержит ожидаемого формата.")
                return "Не удалось обработать ответ от g4f."
        else:
            print("Ответ от g4f имеет неожиданный формат:", response)
            return "Не удалось обработать ответ от g4f."

    except AttributeError as e:
        # Ошибка, если провайдер недоступен
        print(f"Ошибка: Провайдер недоступен: {e}")
        return "Произошла ошибка: Провайдер недоступен."
    except Exception as e:
        # Логирование и возврат сообщения об ошибке
        print(f"Ошибка при использовании g4f: {e}")
        return "Произошла ошибка при генерации ответа с использованием G4F."

def chatgpt_response(prompt):
    try:
        print("Запрос к ChatGPT...")
        # Генерация ответа с помощью OpenAI (GPT-4)
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        # Возврат ответа от OpenAI
        print("Ответ от ChatGPT:", response.choices[0].message['content'])
        return response.choices[0].message['content']
    except Exception as e:
        # Логирование ошибки и возврат сообщения
        print(f"Ошибка при использовании ChatGPT: {e}")
        return "Произошла ошибка при генерации ответа с использованием ChatGPT."
