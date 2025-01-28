from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio

# Замените на ваш токен
API_TOKEN = 'Y7540008294:AAFCR77AHQDAwFwFM2VoV8vWU_HI8R9RBtQ'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    # Создаем клавиатуру с кнопками с использованием ReplyKeyboardBuilder
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Категория 1"))
    builder.add(KeyboardButton(text="Категория 2"))
    builder.add(KeyboardButton(text="Категория 3"))
    builder.add(KeyboardButton(text="Категория 4"))
    builder.adjust(2)  # Располагаем кнопки по 2 в строке

    # Отправляем сообщение с клавиатурой
    await message.answer(
        "Выберите категорию игр:",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )

# Обработчик текстовых сообщений (нажатий на кнопки)
@dp.message(F.text.in_(["Категория 1", "Категория 2", "Категория 3", "Категория 4"]))
async def handle_message(message: types.Message):
    text = message.text

    # В зависимости от выбранной категории отправляем соответствующий ответ
    if text == 'Категория 1':
        await message.answer('Вы выбрали Категорию 1. Вот список игр: Игра 1, Игра 2, Игра 3')
    elif text == 'Категория 2':
        await message.answer('Вы выбрали Категорию 2. Вот список игр: Игра 4, Игра 5, Игра 6')
    elif text == 'Категория 3':
        await message.answer('Вы выбрали Категорию 3. Вот список игр: Игра 7, Игра 8, Игра 9')
    elif text == 'Категория 4':
        await message.answer('Вы выбрали Категорию 4. Вот список игр: Игра 10, Игра 11, Игра 12')

# Обработчик для всех остальных сообщений
@dp.message()
async def handle_other_messages(message: types.Message):
    await message.answer('Пожалуйста, выберите категорию из предложенных.')

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())