import logging
import aiohttp
import asyncio
from config import STEAM_API_KEY, GAMES
from database import add_update, get_subscribed_users, updates_collection, add_tournament, get_upcoming_tournaments
from datetime import datetime
from cachetools import TTLCache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Кэш для оптимизации запросов
cache = TTLCache(maxsize=100, ttl=3600)  # Кэш с TTL 1 час

async def fetch_game_updates(app_id):
    cache_key = f"updates_{app_id}"
    if cache_key in cache:
        logger.info(f"Используем кэш для AppID {app_id}")
        return cache[cache_key]
    
    async with aiohttp.ClientSession() as session:
        url = f"http://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={app_id}&count=5&key={STEAM_API_KEY}"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"Получены обновления для игры с AppID {app_id}: {data}")
                cache[cache_key] = data
                return data
    logger.error(f"Ошибка при получении обновлений для AppID {app_id}")
    return None

async def fetch_game_prices(app_id):
    cache_key = f"prices_{app_id}"
    if cache_key in cache:
        logger.info(f"Используем кэш для цен AppID {app_id}")
        return cache[cache_key]
    
    async with aiohttp.ClientSession() as session:
        url = f"http://store.steampowered.com/api/appdetails?appids={app_id}&key={STEAM_API_KEY}"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if str(app_id) in data and data[str(app_id)]["success"]:
                    price_data = data[str(app_id)]["data"]
                    discount = price_data.get("discount_percent", 0)
                    final_price = price_data.get("price_overview", {}).get("final_formatted", "N/A")
                    cache[cache_key] = {"discount": discount, "price": final_price}
                    return cache[cache_key]
    logger.error(f"Ошибка при получении цен для AppID {app_id}")
    return None

async def check_updates(bot):
    while True:
        for game_name, app_id in GAMES.items():
            updates = await fetch_game_updates(app_id)
            if updates and "appnews" in updates and "newsitems" in updates["appnews"]:
                for news in updates["appnews"]["newsitems"][:3]:
                    news_id = news["gid"]
                    if not updates_collection.find_one({"news_id": news_id}):
                        add_update(
                            news_id=news_id,
                            game_name=game_name,
                            title=news["title"],
                            contents=news["contents"],
                            url=news["url"],
                            date=datetime.fromtimestamp(news["date"])
                        )
                        logger.info(f"Добавлено новое обновление для {game_name} с ID {news_id}")
                        for user in get_subscribed_users():
                            preferences = user.get("preferred_games", [])
                            if game_name in preferences or not preferences:
                                try:
                                    await bot.send_message(
                                        user["user_id"],
                                        f"🔔 Новое обновление {game_name}:\n{news['title']}\n🔗 {news['url']}"
                                    )
                                    logger.info(f"Уведомление отправлено пользователю {user['user_id']}")
                                except Exception as e:
                                    logger.error(f"Ошибка при отправке уведомления пользователю {user['user_id']}: {e}")

            # Проверка скидок с порогом
            price_data = await fetch_game_prices(app_id)
            if price_data and price_data["discount"] >= 20:
                discount_message = f"💰 Скидка на {game_name}! -{price_data['discount']}% Цена: {price_data['price']}. 🔗 https://store.steampowered.com/app/{app_id}"
                for user in get_subscribed_users():
                    preferences = user.get("preferred_games", [])
                    if game_name in preferences or not preferences:
                        try:
                            await bot.send_message(
                                user["user_id"],
                                discount_message
                            )
                            logger.info(f"Уведомление о скидке отправлено пользователю {user['user_id']}")
                        except Exception as e:
                            logger.error(f"Ошибка при отправке уведомления о скидке пользователю {user['user_id']}: {e}")

        # Проверка турниров (раз в день)
        if datetime.now().hour == 0:
            from datetime import timedelta
            tournaments = get_upcoming_tournaments()
            now = datetime.now()
            for tournament in tournaments:
                if (tournament["date"] - now).days <= 7:
                    for user in get_subscribed_users():
                        preferences = user.get("preferred_games", [])
                        if tournament["game"] in preferences or not preferences:
                            try:
                                await bot.send_message(
                                    user["user_id"],
                                    f"🏅 Скоро турнир! {tournament['event_name']} ({tournament['game']})\n"
                                    f"📅 Дата: {tournament['date']}\n🔗 {tournament['url']}"
                                )
                                logger.info(f"Уведомление о турнире отправлено пользователю {user['user_id']}")
                            except Exception as e:
                                logger.error(f"Ошибка при отправке уведомления о турнире пользователю {user['user_id']}: {e}")

        await asyncio.sleep(3600)  # Проверка раз в час