import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Настройки
API_TOKEN = '7540008294:AAFCR77AHQDAwFwFM2VoV8vWU_HI8R9RBtQ'  # Токен вашего Telegram-бота
STEAM_API_KEY = '78A97ED62C016B43824A3F16C36B1D78'   # Ваш Steam API Key (получить на https://steamcommunity.com/dev/apikey)
STEAM_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2"  # API для списка игр
NEWS_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2"  # API для новостей игр

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Список отслеживаемых игр (можно добавить или изменить)
MONITORED_GAMES = {
    730: "Counter-Strike: Global Offensive",  # CS:GO
    570: "Dota 2",
    440: "Team Fortress 2",
    374320: "Rust",
    294100: "Grand Theft Auto V",
    578080: "PUBG",
    892970: "Apex Legends",
}

# Словарь для хранения последних известных новостей
last_known_news = {}

# Функция для получения новостей игры
async def fetch_game_news(app_id):
    params = {
        "appid": app_id,
        "count": 5,  # Количество новостей
        "maxlength": 300,  # Максимальная длина текста новости
        "format": "json",
        "key": STEAM_API_KEY
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(NEWS_URL, params=params) as response:
            data = await response.json()
            if 'appnews' in data and 'newsitems' in data['appnews']:
                return data['appnews']['newsitems']
    return []

# Функция для проверки новых обновлений
async def check_for_updates():
    global last_known_news
    while True:
        updates_found = False
        for app_id, game_name in MONITORED_GAMES.items():
            news_items = await fetch_game_news(app_id)
            if not news_items:
                continue
            for news in news_items:
                news_id = news['gid']  # Уникальный ID новости
                if app_id not in last_known_news or news_id not in last_known_news[app_id]:
                    # Новая новость найдена
                    updates_found = True
                    update_message = (
                        f"🎮 {game_name}\n"
                        f"📝 {news['title']}\n"
                        f"🔗 {news['url']}\n"
                    )
                    print(f"Новое обновление: {update_message}")  # Логирование в консоль

                    # Отправляем уведомление всем пользователям (замените на реальные ID пользователей)
                    user_ids = [123456789]  # Пример ID пользователя
                    for user_id in user_ids:
                        try:
                            # Отправляем каждое обновление как отдельное сообщение
                            await bot.send_message(user_id, update_message)
                        except Exception as e:
                            print(f"Не удалось отправить уведомление пользователю {user_id}: {e}")

                    # Обновляем словарь с известными новостями
                    if app_id not in last_known_news:
                        last_known_news[app_id] = set()
                    last_known_news[app_id].add(news_id)

        if not updates_found:
            print("Обновлений не найдено.")

        # Ждем 10 минут перед следующей проверкой
        await asyncio.sleep(600)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    week_button = InlineKeyboardButton("Последние обновления недели", callback_data="week_updates")
    month_button = InlineKeyboardButton("Последние обновления месяца", callback_data="month_updates")
    keyboard.add(week_button, month_button)

    await message.answer(
        "Привет! Я бот, который следит за обновлениями игр в Steam.\n"
        "Нажмите на кнопку, чтобы увидеть последние обновления:",
        reply_markup=keyboard
    )

# Обработчик нажатия на кнопки
@dp.callback_query_handler(lambda c: c.data in ["week_updates", "month_updates"])
async def handle_updates(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    if callback_query.data == "week_updates":
        time_delta = timedelta(weeks=1)
    elif callback_query.data == "month_updates":
        time_delta = timedelta(days=30)

    start_date = int((datetime.now() - time_delta).timestamp())

    # Отправляем каждое обновление как отдельное сообщение
    for app_id, game_name in MONITORED_GAMES.items():
        news_items = await fetch_game_news(app_id)
        for news in news_items:
            if int(news.get('date', 0)) >= start_date:
                update_message = (
                    f"🎮 {game_name}\n"
                    f"📝 {news['title']}\n"
                    f"🔗 {news['url']}\n"
                )
                try:
                    await bot.send_message(callback_query.from_user.id, update_message)
                except Exception as e:
                    print(f"Не удалось отправить уведомление пользователю {callback_query.from_user.id}: {e}")

    if not news_items:
        await bot.send_message(callback_query.from_user.id, "За выбранный период обновлений не найдено.")

# Запуск бота и фоновой задачи
async def on_startup(dp):
    asyncio.create_task(check_for_updates())  # Запускаем фоновую задачу для отслеживания обновлений

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)