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

# Список отслеживаемых игр
MONITORED_GAMES = {
    730: "Counter-Strike: Global Offensive",  # CS:GO
    570: "Dota 2",
    440: "Team Fortress 2",
    374320: "Rust",
    294100: "Grand Theft Auto V",
    578080: "PUBG",
    892970: "Apex Legends",
}

# Ссылки на категории игр
CATEGORY_LINKS = {
    'action': 'https://store.steampowered.com/category/action/',
    'strategy': 'https://store.steampowered.com/category/strategy?l=russian',
    'rpg': 'https://store.steampowered.com/category/rpg',
    'racing': 'https://store.steampowered.com/category/racing',
}

# Ссылки на категории музыки
MUSIC_LINKS = {
    'chill': 'https://uppbeat.io/music/category/chill',  # Chill music
    'action': 'https://uppbeat.io/browse/collection/fps-action',  # Action music
    'workout': 'https://vk.com/music/playlist/558600949_71',  # Workout music
    'meloman': 'https://rus.hitmotop.com/collection/9414'   # Meloman music
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

# Функция для получения обновлений за указанный период
async def get_updates_for_period(period: str, user_id: int):
    time_deltas = {
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
    }

    if period not in time_deltas:
        return

    start_date = int((datetime.now() - time_deltas[period]).timestamp())
    updates_found = False

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
                    await bot.send_message(user_id, update_message)
                    updates_found = True
                except Exception as e:
                    print(f"Не удалось отправить уведомление пользователю {user_id}: {e}")

    if not updates_found:
        await bot.send_message(user_id, f"За выбранный период ({period}) обновлений не найдено.")

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Создаем кнопки в главном меню
    keyboard = InlineKeyboardMarkup(row_width=1)
    updates_button = InlineKeyboardButton("Отслеживание обновлений", callback_data="updates")
    day_button = InlineKeyboardButton("Обновления за день", callback_data="day_updates")
    week_button = InlineKeyboardButton("Обновления за неделю", callback_data="week_updates")
    month_button = InlineKeyboardButton("Обновления за месяц", callback_data="month_updates")
    extra_features_button = InlineKeyboardButton("Дополнительные возможности", callback_data="extra_features")
    keyboard.add(updates_button, day_button, week_button, month_button, extra_features_button)

    await message.answer(
        "Привет! Я геймерский бот. Я могу отслеживать обновления игр в Steam, показывать обновления за определенный период и предоставлять дополнительные функции.\n"
        "Выберите раздел:",
        reply_markup=keyboard
    )

# Обработчик кнопок для просмотра обновлений за период
@dp.callback_query_handler(lambda c: c.data in ["day_updates", "week_updates", "month_updates"])
async def handle_period_updates(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    period_mapping = {
        "day_updates": "day",
        "week_updates": "week",
        "month_updates": "month",
    }

    period = period_mapping.get(callback_query.data)
    if period:
        await get_updates_for_period(period, callback_query.from_user.id)

# Обработчик кнопки "Дополнительные возможности"
@dp.callback_query_handler(lambda c: c.data == 'extra_features')
async def extra_features(callback_query: types.CallbackQuery):
    # Создаем три кнопки: "Категории игр", "Тренировка аима", "Хочу послушать музыку"
    keyboard = InlineKeyboardMarkup(row_width=1)
    categories_button = InlineKeyboardButton("Категории игр", callback_data='categories')
    aim_training_button = InlineKeyboardButton("Тренировка аима", url="https://app.3daimtrainer.com/quick-play")
    music_button = InlineKeyboardButton("Хочу послушать музыку", callback_data='music')
    back_button = InlineKeyboardButton("Назад", callback_data='back')  # Кнопка "Назад"
    keyboard.add(categories_button, aim_training_button, music_button, back_button)

    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text="Выберите действие:",
        reply_markup=keyboard
    )
    await bot.answer_callback_query(callback_query.id)

# Обработчик кнопки "Назад"
@dp.callback_query_handler(lambda c: c.data == 'back')
async def back_to_main_menu(callback_query: types.CallbackQuery):
    # Создаем кнопки в главном меню
    keyboard = InlineKeyboardMarkup(row_width=1)
    updates_button = InlineKeyboardButton("Отслеживание обновлений", callback_data="updates")
    day_button = InlineKeyboardButton("Обновления за день", callback_data="day_updates")
    week_button = InlineKeyboardButton("Обновления за неделю", callback_data="week_updates")
    month_button = InlineKeyboardButton("Обновления за месяц", callback_data="month_updates")
    extra_features_button = InlineKeyboardButton("Дополнительные возможности", callback_data="extra_features")
    keyboard.add(updates_button, day_button, week_button, month_button, extra_features_button)

    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text="Выберите раздел:",
        reply_markup=keyboard
    )
    await bot.answer_callback_query(callback_query.id)

# Обработчик кнопки "Категории игр"
@dp.callback_query_handler(lambda c: c.data == 'categories')
async def send_categories(callback_query: types.CallbackQuery):
    # Создаем кнопки для разных категорий игр
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Экшен", callback_data='action'),
        InlineKeyboardButton("Стратегии", callback_data='strategy'),
        InlineKeyboardButton("РПГ", callback_data='rpg'),
        InlineKeyboardButton("Гонки", callback_data='racing')
    ]
    back_button = InlineKeyboardButton("Назад", callback_data='back')  # Кнопка "Назад"
    keyboard.add(*buttons, back_button)

    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text="Выберите категорию игр:",
        reply_markup=keyboard
    )
    await bot.answer_callback_query(callback_query.id)

# Обработчик выбора категории игр
@dp.callback_query_handler(lambda c: c.data in ['action', 'strategy', 'rpg', 'racing'])
async def process_category(callback_query: types.CallbackQuery):
    category = callback_query.data
    link = CATEGORY_LINKS.get(category, 'https://example.com')  # Если категория не найдена, используется дефолтная ссылка
    await bot.send_message(
        callback_query.from_user.id,
        f"Вы выбрали категорию: {category.capitalize()}\nСсылка: {link}"
    )
    await bot.answer_callback_query(callback_query.id)

# Обработчик кнопки "Хочу послушать музыку"
@dp.callback_query_handler(lambda c: c.data == 'music')
async def music(callback_query: types.CallbackQuery):
    # Создаем кнопки для разных категорий музыки
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Почилить на раслабоне", url=MUSIC_LINKS['chill']),
        InlineKeyboardButton("Экшен под биток", url=MUSIC_LINKS['action']),
        InlineKeyboardButton("Фонк в качалочку", url=MUSIC_LINKS['workout']),
        InlineKeyboardButton("Меломан", url=MUSIC_LINKS['meloman'])
    ]
    back_button = InlineKeyboardButton("Назад", callback_data='back')  # Кнопка "Назад"
    keyboard.add(*buttons, back_button)

    await bot.send_message(
        callback_query.from_user.id,
        "Выберите плейлист, который хотите послушать:",
        reply_markup=keyboard
    )
    await bot.answer_callback_query(callback_query.id)

# Запуск фоновой задачи для отслеживания обновлений
async def on_startup(dp):
    asyncio.create_task(check_for_updates())  # Запускаем фоновую задачу для отслеживания обновлений

# Обработчик текстовых сообщений
@dp.message_handler()
async def echo(message: types.Message):
    user_message = message.text.lower()
    if 'привет' in user_message:
        await bot.send_message(message.chat.id, 'https://rutube.ru/video/2c0e40c8bbeb82da6d35600f9bfd162f/')
    elif 'как дела' in user_message:
        await bot.send_message(message.chat.id, 'У меня все хорошо, спасибо!')
    else:
        await bot.send_message(message.chat.id, 'Извините, я не понимаю ваш вопрос.')

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
