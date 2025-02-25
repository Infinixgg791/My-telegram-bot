import json
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime

API_TOKEN = '7803421682:AAGw_ESeD5AjmIMeLJCZ9FwZ0gIV-HqBgYU'  # Ваш токен бота
ADMIN_CHAT_ID = 7693328161  # Ваш Telegram ID
PROFILE_FILE = '.profiles.json'  # Скрытый файл для хранения профилей

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

# Определяем состояния
class SupportStates(StatesGroup):
    waiting_for_support_message = State()
    waiting_for_admin_response = State()  # Новое состояние для ожидания ответа администратора

# Загружаем профили из файла
def load_profiles():
    try:
        with open(PROFILE_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Сохраняем профили в файл
def save_profiles(profiles):
    with open(PROFILE_FILE, 'w') as file:
        json.dump(profiles, file)

profiles = load_profiles()  # Загружаем профили при старте бота

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("👋 Привет! Нажмите кнопку, чтобы получить файлы.")
    # Создаем кнопки с эмодзи
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_files = KeyboardButton("📁 Файлы 📁")
    button_support = KeyboardButton("📌 Поддержка 📌")
    button_instruction = KeyboardButton("❓ Инструкция ❓")
    button_profile = KeyboardButton("🧸 Профиль 🧸")  # Кнопка "Профиль" с эмодзи

    # Добавляем кнопки в клавиатуру
    keyboard.add(button_files, button_support, button_instruction)  # Три кнопки в одном ряду
    keyboard.add(button_profile)  # Кнопка "Профиль" в отдельном ряду, занимающая полную ширину

    await message.reply("👋 Привет! Нажмите кнопку, чтобы получить файлы.", reply_markup=keyboard)

# Обработчик для профиля
@dp.message_handler(lambda message: message.text == "🧸 Профиль 🧸")
async def profile(message: types.Message):
    user_id = str(message.from_user.id)

    if user_id not in profiles:
        # Создаем профиль
        creation_date = datetime.now().strftime('%d-%m-%Y')
        profiles[user_id] = {
            "username": message.from_user.username,
            "registered": True,
            "creation_date": creation_date
        }
        save_profiles(profiles)  # Сохраняем профили в файл
        await message.answer(f"✅ Профиль создан\nДата создания: {creation_date}")
    else:
        # Отправляем информацию о профиле
        user_info = profiles[user_id]
        username = user_info['username']
        creation_date = user_info['creation_date']

        # Формируем текст сообщения
        profile_text = (
            f"🧸 Профиль:\n"
            f"▫️ ID: {user_id}\n"
            f"▫️ Юзернейм: @{username}\n"
            f"▫️ Дата создания: {creation_date}"
        )

        await message.answer(profile_text)

@dp.message_handler(lambda message: message.text == "📁 Файлы 📁")
async def send_files(message: types.Message):
    await message.answer("Вот ваши файлы:")
    
    for message_id in [620, 623]:  # Замените на ваши ID
        try:
            await bot.forward_message(chat_id=message.chat.id, from_chat_id='@quickggcheats', message_id=message_id)
        except Exception as e:
            await message.answer(f"Ошибка при пересылке сообщения {message_id}: {str(e)}")

@dp.message_handler(lambda message: message.text == "📌 Поддержка 📌")
async def support(message: types.Message):
    await message.answer("Пожалуйста, напишите ваше сообщение в поддержку. Для выхода нажмите 'Выход'.")
    await SupportStates.waiting_for_support_message.set()  # Устанавливаем состояние ожидания сообщения
    users[message.from_user.id] = message.chat.id  # Сохраняем ID чата пользователя

@dp.message_handler(lambda message: message.text == "❓ Инструкция ❓")
async def instruction(message: types.Message):
    instruction_text = (
        "🔴 Скачивайте Gspace 🔴\n"
        "⭕ Импортируйте в него GameGuardian и Matreshka RP ⭕\n"
        "💎 Заходите в GameGuardian 💎\n"
        "🔹 Затем заходите в Матрешку РП и выбираете в GameGuardian процесс игры Matreshka RP (НЕ Metrica) 🔹\n"
        "🌀 Запускаете скрипт, в правом верхнем углу есть значок play, нажимаете на него, затем нажмите на '...' три точки, выберите Lua файл и запустите 🌀"
    )
    await message.answer(instruction_text)

@dp.message_handler(state=SupportStates.waiting_for_support_message, content_types=types.ContentTypes.TEXT)
async def process_support_message(message: types.Message, state: FSMContext):
    if message.text.lower() == "выход":
        await message.answer("Выход из режима поддержки.")
        await state.finish()  # Завершаем состояние
    else:
        try:
            # Отправляем сообщение вам в личные сообщения
            await bot.send_message(
                ADMIN_CHAT_ID,
                f"🔔 Новое сообщение 🔔:\n"
                f"От пользователя: {message.from_user.username}\n"
                f"ID пользователя: {message.from_user.id}\n"
                f"Сообщение: {message.text}\n"
                f"Ответьте этому пользователю: /reply {message.from_user.id} <ваш ответ>"
            )
            await message.answer("Ваше сообщение отправлено в поддержку. Спасибо!")
        except Exception as e:
            await message.answer(f"Произошла ошибка при отправке сообщения: {str(e)}")
        finally:
            await state.finish()  # Завершаем состояние

@dp.message_handler(lambda message: message.text.startswith('/reply'), state='*')
async def reply_to_user(message: types.Message):
    # Проверяем, является ли отправитель администратором
    if message.from_user.id == ADMIN_CHAT_ID:
        parts = message.text.split(' ', 2)  # Разбиваем сообщение на части
        if len(parts) < 3:
            await message.answer("Используйте формат: /reply <user_id> <ваш ответ>")
            return
        
        user_id = int(parts[1])  # Получаем ID пользователя
        reply_text = parts[2]  # Получаем текст ответа

        if user_id in users:
            await bot.send_message(
                users[user_id],
                f"🔔 Новое сообщение от поддержки 🔔:\n{reply_text} 🔹"
            )
            await message.answer("Ответ отправлен пользователю.")
        else:
            await message.answer("Пользователь не найден.")
    else:
        await message.answer("У вас нет прав для отправки ответов.")

@dp.message_handler()
async def unknown_command(message: types.Message):
    await message.answer("⁉️ Я не знаю такую команду...")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
