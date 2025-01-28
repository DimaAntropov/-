

# Функция для обработки команды /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Привет! Я бот, который умеет:\n"
        "- Показывать это сообщение по команде /start\n"
        "- Выполнять другие команды, которые ты добавишь!"
    )

# Основная функция для запуска бота
def main() -> None:
    # Вставьте сюда ваш токен
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрируем обработчик команды /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Запускаем бота
    updater.start_polling()

    # Работаем до тех пор, пока не будет нажата комбинация Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()