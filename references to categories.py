from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Вставьте сюда ваш токен
API_TOKEN = 'API_TOKEN'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Ссылки на категории игр (замените на реальные ссылки)
CATEGORY_LINKS = {
    'action': 'https://store.steampowered.com/category/action/',
    'strategy': 'https://store.steampowered.com/category/strategy?l=russian',
    'rpg': 'https://store.steampowered.com/category/rpg',
    'racing': 'https://store.steampowered.com/category/racing',
}

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await bot.send_message(
        message.chat.id,
        "Привет! Я геймерский_бот. Я могу посоветовать тебе игры из категорий, которые ты выберешь, и у меня ты можешь найти все игровые новинки и новости о них."
    )

# Обработчик команды /категории
@dp.message_handler(commands=['категории'])
async def send_categories(message: types.Message):
    # Создаем кнопки для разных категорий игр
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Экшен", callback_data='action'),
        InlineKeyboardButton("Стратегии", callback_data='strategy'),
        InlineKeyboardButton("РПГ", callback_data='rpg'),
        InlineKeyboardButton("Гонки", callback_data='racing')
    ]
    keyboard.add(*buttons)
    # Отправляем сообщение с кнопками
    await message.answer("Выберите категорию игр:", reply_markup=keyboard)

# Обработчик нажатий на кнопки
@dp.callback_query_handler(lambda c: c.data)
async def process_callback(callback_query: types.CallbackQuery):
    category = callback_query.data
    # Получаем ссылку на категорию
    link = CATEGORY_LINKS.get(category, 'https://example.com')  # Если категория не найдена, используется дефолтная ссылка
    # Отправляем сообщение с ссылкой
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        f"Вы выбрали категорию: {category.capitalize()}\nСсылка: {link}"
    )

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
    executor.start_polling(dp, skip_updates=True)
