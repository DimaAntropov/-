import asyncio
from aiogram import Bot, Dispatcher
from config import TELEGRAM_TOKEN
from handlers import register_handlers
from game_news import check_updates

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

async def main():
    # Регистрация обработчиков
    register_handlers(dp)
    # Запуск проверки обновлений в фоне
    asyncio.create_task(check_updates(bot))
    # Запуск диспетчера
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())