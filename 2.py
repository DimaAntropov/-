from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

API_TOKEN = '7540008294:AAFCR77AHQDAwFwFM2VoV8vWU_HI8R9RBtQ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await bot.send_message(message.chat.id, "Привет! Я простой бот. Задайте мне вопрос.")

@dp.message_handler()
async def echo(message: types.Message):
    print(message.from_user.first_name,message.from_user.id)
    user_message = message.text.lower()
    if 'что ты умеешь' in user_message:
        await bot.send_message(message.chat.id, ''''
я умею регистрировать пользователей
я умею хранить секреты''')
    elif 'как дела' in user_message:
        await bot.send_message(message.chat.id, 'У меня все хорошо, спасибо!')
    else:
        await bot.send_message(message.chat.id, 'Извините, я не понимаю ваш вопрос.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
