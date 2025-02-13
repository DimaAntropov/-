import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor

# Настройки
API_TOKEN = ''
STEAM_API_KEY = 'ДИМЕ НЕ ЗАЧЕТ, ОН НЕЧЕГО НЕ ДЕЛАЛ!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
STEAM_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2"
NEWS_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

MONITORED_GAMES = {
    730: "Counter-Strike: Global Offensive",
    570: "Dota 2",
    440: "Team Fortress 2",
    374320: "Rust",
    294100: "Grand Theft Auto V",
    578080: "PUBG",
    892970: "Apex Legends",
}

CATEGORY_LINKS = {
    'action': 'https://store.steampowered.com/category/action/',
    'strategy': 'https://store.steampowered.com/category/strategy?l=russian',
    'rpg': 'https://store.steampowered.com/category/rpg',
    'racing': 'https://store.steampowered.com/category/racing',
}

MUSIC_LINKS = {
    'chill': 'https://uppbeat.io/music/category/chill',
    'action': 'https://uppbeat.io/browse/collection/fps-action',
    'workout': 'https://vk.com/music/playlist/558600949_71',
    'meloman': 'https://rus.hitmotop.com/collection/9414'
}

last_known_news = {}

async def fetch_game_news(app_id):
    params = {
        "appid": app_id,
        "count": 5,
        "maxlength": 300,
        "format": "json",
        "key": STEAM_API_KEY
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(NEWS_URL, params=params) as response:
            data = await response.json()
            if 'appnews' in data and 'newsitems' in data['appnews']:
                return data['appnews']['newsitems']
    return []

async def check_for_updates():
    global last_known_news
    while True:
        updates_found = False
        for app_id, game_name in MONITORED_GAMES.items():
            news_items = await fetch_game_news(app_id)
            if not news_items:
                continue
            for news in news_items:
                news_id = news['gid']
                if app_id not in last_known_news or news_id not in last_known_news[app_id]:
                    updates_found = True
                    update_message = (
                        f"🎮 {game_name}\n"
                        f"📝 {news['title']}\n"
                        f"🔗 {news['url']}\n"
                    )
                    logging.info(f"Новое обновление: {update_message}")

                    user_ids = [123456789]
                    for user_id in user_ids:
                        try:
                            await bot.send_message(user_id, update_message)
                        except Exception as e:
                            logging.error(f"Ошибка отправки: {e}")

                    if app_id not in last_known_news:
                        last_known_news[app_id] = set()
                    last_known_news[app_id].add(news_id)

        if not updates_found:
            logging.info("Обновлений не найдено.")

        await asyncio.sleep(600)

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
                    logging.error(f"Ошибка: {e}")

    if not updates_found:
        await bot.send_message(user_id, f"Нет обновлений за {period}.")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Отслеживание обновлений", callback_data="updates"),
        InlineKeyboardButton("Обновления за день", callback_data="day_updates"),
        InlineKeyboardButton("Обновления за неделю", callback_data="week_updates"),
        InlineKeyboardButton("Обновления за месяц", callback_data="month_updates"),
        InlineKeyboardButton("Дополнительные возможности", callback_data="extra_features")
    ]
    keyboard.add(*buttons)

    await message.answer(
        "Привет! Я геймерский бот. Выберите раздел:",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data in ["day_updates", "week_updates", "month_updates"])
async def handle_period_updates(callback_query: types.CallbackQuery):
    period_mapping = {
        "day_updates": "day",
        "week_updates": "week",
        "month_updates": "month",
    }
    period = period_mapping.get(callback_query.data)
    if period:
        await get_updates_for_period(period, callback_query.from_user.id)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda c: c.data == 'extra_features')
async def extra_features(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Категории игр", callback_data='categories'),
        InlineKeyboardButton("Тренировка аима", url="https://app.3daimtrainer.com/quick-play"),
        InlineKeyboardButton("Хочу послушать музыку", callback_data='music'),
        InlineKeyboardButton("Назад", callback_data='back')
    ]
    keyboard.add(*buttons)

    await bot.edit_message_text(
        "Выберите действие:",
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=keyboard
    )
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda c: c.data == 'back')
async def back_to_main_menu(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Отслеживание обновлений", callback_data="updates"),
        InlineKeyboardButton("Обновления за день", callback_data="day_updates"),
        InlineKeyboardButton("Обновления за неделю", callback_data="week_updates"),
        InlineKeyboardButton("Обновления за месяц", callback_data="month_updates"),
        InlineKeyboardButton("Дополнительные возможности", callback_data="extra_features")
    ]
    keyboard.add(*buttons)

    await bot.edit_message_text(
        "Выберите раздел:",
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=keyboard
    )
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda c: c.data == 'categories')
async def send_categories(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Экшен", callback_data='action'),
        InlineKeyboardButton("Стратегии", callback_data='strategy'),
        InlineKeyboardButton("РПГ", callback_data='rpg'),
        InlineKeyboardButton("Гонки", callback_data='racing'),
        InlineKeyboardButton("Назад", callback_data='back')
    ]
    keyboard.add(*buttons)

    await bot.edit_message_text(
        "Выберите категорию игр:",
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=keyboard
    )
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda c: c.data in ['action', 'strategy', 'rpg', 'racing'])
async def process_category(callback_query: types.CallbackQuery):
    category = callback_query.data
    link = CATEGORY_LINKS.get(category, 'https://example.com')
    await bot.send_message(
        callback_query.from_user.id,
        f"Категория: {category.capitalize()}\nСсылка: {link}"
    )
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda c: c.data == 'music')
async def music(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Почилить на раслабоне", url=MUSIC_LINKS['chill']),
        InlineKeyboardButton("Экшен под биток", url=MUSIC_LINKS['action']),
        InlineKeyboardButton("Фонк в качалочку", url=MUSIC_LINKS['workout']),
        InlineKeyboardButton("Меломан", url=MUSIC_LINKS['meloman']),
        InlineKeyboardButton("Назад", callback_data='back')
    ]
    keyboard.add(*buttons)

    await bot.send_message(
        callback_query.from_user.id,
        "Выберите плейлист:",
        reply_markup=keyboard
    )
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler()
async def echo(message: types.Message):
    user_message = message.text.lower()
    if 'привет' in user_message:
        await bot.send_message(message.chat.id, 'https://rutube.ru/video/2c0e40c8bbeb82da6d35600f9bfd162f/')
    elif 'как дела' in user_message:
        await bot.send_message(message.chat.id, 'Всё отлично!')
    else:
        await bot.send_message(message.chat.id, 'Не понимаю команду.')

async def on_startup(_):
    asyncio.create_task(check_for_updates())

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True) 
