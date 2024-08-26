import os

import telebot
from openai import OpenAI
from gtts import gTTS


# Инициализация клиента API OpenAI с вашим API ключом
openai_client = OpenAI(
    api_key="YOUR_OPENAI_TOKEN",
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Замените 'YOUR_BOT_API_TOKEN' на ваш токен API, который вы получили от BotFather
API_TOKEN = "YOUR_BOT_API_TOKEN"

bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения истории разговора с каждым пользователем
conversation_histories = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я ваш Telegram-бот. Как я могу вам помочь?")

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "Вот список доступных команд:\n"
        "/start - начать взаимодействие с ботом\n"
        "/help - получить справку по командам\n"
        "/perevorot <ваш текст> - перевернуть текст\n"
        "/caps <ваш текст> - преобразовать текст в заглавные буквы\n"
        "/cut <ваш текст> - удалить гласные буквы в тексте\n"
        "/count <ваш текст> - подсчитать количество символов в тексте\n"
    )
    bot.reply_to(message, help_text)

# Обработчик команды /perevorot
@bot.message_handler(commands=['perevorot'])
def send_reversed(message):
    # Получаем текст сообщения без команды
    text_to_reverse = message.text[len('/perevorot '):]

    # Переворачиваем текст
    reversed_text = text_to_reverse[::-1]

    # Отправляем перевёрнутый текст обратно пользователю
    bot.reply_to(message, reversed_text)
    
# Обработчик команды /caps
@bot.message_handler(commands=['caps'])
def send_caps(message):
    text_to_caps = message.text[len('/caps '):]
    caps_text = text_to_caps.upper()
    bot.reply_to(message, caps_text)

# Обработчик команды /cut
@bot.message_handler(commands=['cut'])
def send_cut(message):
    text_to_cut = message.text[len('/cut '):]
    vowels = "аеёиоуыэюяАЕЁИОУЫЭЮЯaeiouAEIOU"
    cut_text = ''.join([char for char in text_to_cut if char not in vowels])
    bot.reply_to(message, cut_text)

# Обработчик команды /count
@bot.message_handler(commands=['count'])
def send_count(message):
    # Получаем текст сообщения без команды
    text_to_count = message.text[len('/count '):]

    # Подсчитываем количество символов в тексте
    count = len(text_to_count)

    # Отправляем обратно количество символов
    bot.reply_to(message, f"Количество символов в вашем сообщении: {count}")

@bot.message_handler(commands=['voice'])
def send_voice(message):
    text = message.text[7:]  # Получение текста после команды /voice
    tts = gTTS(text=text, lang='ru')  # Создание объекта с текстом и выбранным языком
    tts.save("voice.mp3")  # Сохранение озвученного текста в файл voice.mp3
    voice = open("voice.mp3", 'rb')  # Открытие файла с озвученным текстом
    bot.send_voice(message.chat.id, voice)  # Отправка озвученного текста пользователю
    os.remove("voice.mp3")  # Удаление временного файла с озвученным текстом

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_input = message.text

    # Если история для пользователя не существует, создаем новую
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []

    # Добавление ввода пользователя в историю разговора
    conversation_history = conversation_histories[user_id]
    conversation_history.append({"role": "user", "content": user_input})

    # Отправка запроса в нейронную сеть
    chat_completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=conversation_history
    )

    # Извлечение и ответ на сообщение пользователя
    ai_response_content = chat_completion.choices[0].message.content
    bot.reply_to(message, ai_response_content)

    # Добавление ответа нейронной сети в историю разговора
    conversation_history.append({"role": "system", "content": "отвечай в стиле романтической поэзии"})
    
# Запуск бота
if __name__ == '__main__':
    print("Бот запущен и готов к работе...")
    bot.polling(none_stop=True)
