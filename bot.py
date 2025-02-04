
API_TOKEN = 'API_TOKEN'

    

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await bot.send_message(message.chat.id, "Привет! Я геймерский_бот. Я могу посоветовать тебе игры из категорий каторые ты выберешь и у меня вы можете найти все игровые навинки и новости о них. Вот команды которые у меня есть /start, /категории, /тренеровка аима.")

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    print(message)
    document_id = message.document.file_id
    file_info = await bot.get_file(document_id)
    await bot.download_file(file_info.file_path, f"./downloads/{message.document.file_name}")
    await bot.send_message(message.chat.id, f"Файл {message.document.file_name} получен и сохранен.")

@dp.message_handler(lambda message: message.text.lower() == "привет")
async def greet_user(message: types.Message):
    await message.reply("Привет! Как дела?")

@dp.message_handler()
async def echo(message: types.Message):
    print(message)
    user_message = message.text.lower()
    if 'привет' in user_message:
        await bot.send_message(message.chat.id, 'https://rutube.ru/video/2c0e40c8bbeb82da6d35600f9bfd162f/')
    elif 'как дела' in user_message:
        await bot.send_message(message.chat.id, 'У меня все хорошо, спасибо!')
    else:
        await bot.send_message(message.chat.id, 'Извините, я не понимаю ваш вопрос.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)











