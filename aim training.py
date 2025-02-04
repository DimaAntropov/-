from aiogram import Bot, Dispatcher, executor, types

# Создайте экземпляр бота и диспетчера
API_TOKEN = "API_TOKEN"  # Замените на ваш токен
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Обработчик команды /тренировка
@dp.message_handler(commands=['тренировка'])
async def тренировка(message: types.Message):
    # Создаем кнопку
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Тренировка аима", url="https://app.3daimtrainer.com/quick-play")
    keyboard.add(button)

    # Отправляем сообщение с кнопкой
    await message.answer("Нажмите на кнопку для начала тренировки аима:", reply_markup=keyboard)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
