from aiogram import Dispatcher, types, Bot
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards import get_main_keyboard, get_period_keyboard, get_additional_keyboard, get_quiz_keyboard, get_settings_keyboard, get_tracking_keyboard, get_notifications_keyboard, get_feedback_keyboard, get_back_to_period_keyboard, get_back_to_main_keyboard
from database import add_user, subscribe_user, unsubscribe_user, get_updates_by_period, add_quiz_question, get_random_quiz_question, update_user_preferences, get_user_preferences, update_user_score, get_user_score, get_leaderboard, get_update_stats, add_tournament, get_upcoming_tournaments, get_subscribed_users, get_user_by_id
from config import GAMES, STEAM_API_KEY, DEVELOPER_CHAT_ID
from datetime import datetime, timedelta
import aiohttp
import asyncio
from cachetools import TTLCache

# Кэш для оптимизации запросов
cache = TTLCache(maxsize=100, ttl=3600)

# Состояния FSM
class UserState(StatesGroup):
    selecting_period = State()
    answering_quiz = State()
    selecting_settings = State()
    selecting_tracking = State()
    selecting_feedback = State()
    viewing_game_updates = State()  # Для просмотра обновлений игры

def register_handlers(dp: Dispatcher) -> None:
    """Регистрирует обработчики событий для бота."""

    @dp.message(Command("start"))
    async def start_command(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        add_user(user_id)
        # Send the initial message and store its message_id in the state
        sent_message = await message.answer(
            "🌟 Привет! Я бот для отслеживания обновлений игр в Steam! 🌟\n"
            "Выбери действие из меню ниже, чтобы начать:",
            reply_markup=get_main_keyboard()
        )
        await state.update_data(message_id=sent_message.message_id)
        await state.clear()  # Clear any previous state

    @dp.message(Command("help"))
    async def help_command(message: types.Message, state: FSMContext):
        """Обработчик команды /help."""
        await message.answer(
            "❓ **Помощь по боту**\n\n"
            "Я — твой помощник для отслеживания обновлений игр в Steam! Вот что я умею:\n\n"
            "🔔 *Обновления* — показываю последние новости по твоим любимым играм.\n"
            "🎮 *Дополнительно* — предоставляю ссылки на категории игр в Steam.\n"
            "⚙️ *Настройки* — настрой отслеживание игр и уведомления.\n"
            "📊 *Статистика* — показываю статистику обновлений за выбранный период.\n"
            "🏆 *Таблица лидеров* — смотри топ игроков викторины.\n"
            "🏅 *Турниры* — узнай о предстоящих игровых турнирах.\n"
            "⭐ *Рекомендации* — предложу новые игры, которые могут тебе понравиться.\n"
            "📩 *Обратная связь* — поделись своими идеями или сообщи о проблемах.\n\n"
            "Если вы хотите начать, просто нажмите /start 😊"
        )
        await state.clear()

    @dp.callback_query(lambda c: c.data == "updates")
    async def show_updates(callback: types.CallbackQuery, state: FSMContext):
        preferences = get_user_preferences(callback.from_user.id)
        if not preferences:
            await callback.message.edit_text(
                "🔔 Сначала настройте предпочтения в разделе '⚙️ Настройки' -> '👀 Отслеживание'.",
                reply_markup=get_main_keyboard()
            )
            return
        await callback.message.edit_text(
            "🕒 Выбери период для просмотра обновлений:",
            reply_markup=get_period_keyboard()
        )
        await state.set_state(UserState.selecting_period)
        await state.update_data(context="updates")
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "back_to_period")
    async def back_to_period(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🕒 Выбери период для просмотра обновлений:",
            reply_markup=get_period_keyboard()
        )
        await state.set_state(UserState.selecting_period)
        await state.update_data(context="updates")
        await callback.answer()

    @dp.callback_query(lambda c: c.data.startswith("period_"))
    async def process_period(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        context = data.get("context")
        period = callback.data.replace("period_", "")
        now = datetime.now()
        if period == "day":
            delta = timedelta(days=1)
        elif period == "week":
            delta = timedelta(weeks=1)
        elif period == "month":
            delta = timedelta(days=30)
        else:
            await callback.message.edit_text("❌ Неверный выбор!", reply_markup=get_main_keyboard())
            await state.clear()
            return

        if context == "updates":
            updates = get_updates_by_period(now - delta)
            preferences = get_user_preferences(callback.from_user.id)
            response = "🔔 Последние обновления:\n\n"
            for update in updates:
                if update["game"] in preferences:
                    response += f"🎮 {update['game']}: {update['title']}\n🔗 {update['url']}\n\n"
            await callback.message.edit_text(
                response or "⚠️ Нет обновлений за этот период.",
                reply_markup=get_back_to_period_keyboard()  # Добавляем кнопку "Назад"
            )
        elif context == "stats":
            stats = get_update_stats(now - delta)
            buttons = []
            response = f"📊 Статистика обновлений (за {period}):\n\n"
            for stat in stats:
                game = stat['_id']
                count = stat['count']
                response += f"🎮 {game}: {count} обновлений\n"
                buttons.append([types.InlineKeyboardButton(text=f"🎮 {game} ({count} обновлений)", callback_data=f"view_updates_{game}")])
            buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
            await callback.message.edit_text(
                response or "⚠️ Нет данных за этот период.",
                reply_markup=keyboard
            )
            await state.update_data(period=period)  # Сохраняем период для использования в следующем шаге

        await state.set_state(UserState.viewing_game_updates)
        await callback.answer()

    @dp.callback_query(lambda c: c.data.startswith("view_updates_"))
    async def view_game_updates(callback: types.CallbackQuery, state: FSMContext):
        """Обработчик для просмотра обновлений конкретной игры."""
        game = callback.data.replace("view_updates_", "")
        data = await state.get_data()
        period = data.get("period", "month")  # По умолчанию месяц, если что-то пошло не так
        now = datetime.now()
        if period == "day":
            delta = timedelta(days=1)
        elif period == "week":
            delta = timedelta(weeks=1)
        elif period == "month":
            delta = timedelta(days=30)
        else:
            delta = timedelta(days=30)

        updates = get_updates_by_period(now - delta)
        response = f"🔔 Обновления для {game} (за {period}):\n\n"
        game_updates = [update for update in updates if update["game"] == game]
        for update in game_updates:
            response += f"📌 {update['title']}\n🔗 {update['url']}\n\n"

        buttons = [[types.InlineKeyboardButton(text="🔙 Назад", callback_data="stats")]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(
            response or f"⚠️ Нет обновлений для {game} за этот период.",
            reply_markup=keyboard
        )
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "additional")
    async def additional_features(callback: types.CallbackQuery):
        await callback.message.edit_text(
            "🎮 Дополнительные возможности:",
            reply_markup=get_additional_keyboard()
        )
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "settings")
    async def show_settings(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "⚙️ Выберите раздел настроек:",
            reply_markup=get_settings_keyboard()
        )
        await state.set_state(UserState.selecting_settings)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "back_to_settings")
    async def back_to_settings(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "⚙️ Выберите раздел настроек:",
            reply_markup=get_settings_keyboard()
        )
        await state.set_state(UserState.selecting_settings)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "tracking")
    async def show_tracking(callback: types.CallbackQuery, state: FSMContext):
        preferences = get_user_preferences(callback.from_user.id)
        await state.update_data(preferences=preferences)  # Сохраняем начальные предпочтения в состояние
        await callback.message.edit_text(
            "👀 Выберите игры для отслеживания:\n(Если вы ещё не выбрали игры, отметьте те, которые хотите отслеживать, и нажмите 💾 Сохранить.)",
            reply_markup=get_tracking_keyboard(preferences)
        )
        await state.set_state(UserState.selecting_tracking)
        await callback.answer()

    @dp.callback_query(lambda c: c.data.startswith("setting_"))
    async def toggle_setting(callback: types.CallbackQuery, state: FSMContext):
        game = callback.data.replace("setting_", "")
        data = await state.get_data()
        preferences = data.get("preferences", [])  # Получаем текущие предпочтения из состояния
        if game in preferences:
            preferences.remove(game)
        else:
            preferences.append(game)
        await state.update_data(preferences=preferences)  # Обновляем предпочтения в состоянии
        current_state = await state.get_state()
        if current_state == UserState.selecting_tracking.state:
            await callback.message.edit_text(
                "👀 Выберите игры для отслеживания:\n(Если вы ещё не выбрали игры, отметьте те, которые хотите отслеживать, и нажмите 💾 Сохранить.)",
                reply_markup=get_tracking_keyboard(preferences)
            )
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "select_all_categories")
    async def select_all_categories(callback: types.CallbackQuery, state: FSMContext):
        """Обработчик для кнопки 'Выбрать все категории'."""
        preferences = list(GAMES.keys())  # Выбираем все игры из GAMES
        await state.update_data(preferences=preferences)  # Сохраняем в состояние
        current_state = await state.get_state()
        if current_state == UserState.selecting_tracking.state:
            await callback.message.edit_text(
                "👀 Выберите игры для отслеживания:\n(Если вы ещё не выбрали игры, отметьте те, которые хотите отслеживать, и нажмите 💾 Сохранить.)",
                reply_markup=get_tracking_keyboard(preferences)
            )
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "save_settings")
    async def save_settings(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        preferences = data.get("preferences", [])  # Получаем предпочтения из состояния
        update_user_preferences(callback.from_user.id, preferences)  # Сохраняем в базу данных
        await callback.message.edit_text(
            "💾 Настройки отслеживания сохранены!",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "cancel_tracking")
    async def cancel_tracking(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🌟 Вы вернулись в главное меню без сохранения изменений!",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "notifications")
    async def show_notifications(callback: types.CallbackQuery):
        await callback.message.edit_text(
            "🔔 Управление уведомлениями:",
            reply_markup=get_notifications_keyboard()
        )
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "subscribe")
    async def subscribe(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        user = get_user_by_id(user_id)
        if not user:
            add_user(user_id)  # Добавляем только если пользователя нет
            await callback.message.edit_text(
                "✅ Вы подписались на уведомления.",
                reply_markup=get_main_keyboard()
            )
        elif not user.get("subscribed", False):
            subscribe_user(user_id)
            await callback.message.edit_text(
                "✅ Вы подписались на уведомления.",
                reply_markup=get_main_keyboard()
            )
        else:
            await callback.message.edit_text(
                "ℹ️ Вы уже подписаны на уведомления.",
                reply_markup=get_main_keyboard()
            )
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "unsubscribe")
    async def unsubscribe(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        user = get_user_by_id(user_id)
        if user and user.get("subscribed", True):
            unsubscribe_user(user_id)
            await callback.message.edit_text(
                "❌ Вы отписались от уведомлений.",
                reply_markup=get_main_keyboard()
            )
        else:
            await callback.message.edit_text(
                "ℹ️ Вы уже отписаны от уведомлений.",
                reply_markup=get_main_keyboard()
            )
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "quiz")
    async def start_quiz(callback: types.CallbackQuery, state: FSMContext):
        quiz = get_random_quiz_question()
        if quiz:
            await state.update_data(quiz_id=quiz["_id"], correct_answer=quiz["correct_answer"])
            await callback.message.edit_text(
                f"❓ Угадайте игру по описанию:\n{quiz['question']}",
                reply_markup=get_quiz_keyboard(quiz["options"])
            )
            await state.set_state(UserState.answering_quiz)
        else:
            await callback.message.edit_text(
                "⚠️ Вопросы для викторины пока недоступны.",
                reply_markup=get_main_keyboard()
            )
        await callback.answer()

    @dp.callback_query(lambda c: c.data.startswith("quiz_answer_"))
    async def process_quiz_answer(callback: types.CallbackQuery, state: FSMContext):
        user_answer = callback.data.replace("quiz_answer_", "")
        user_data = await state.get_data()
        correct_answer = user_data.get("correct_answer")

        if user_answer == correct_answer:
            user_id = callback.from_user.id
            update_user_score(user_id, 1)
            await callback.message.edit_text(
                "✅ Правильно! Отличная работа! (+1 очко)",
                reply_markup=get_back_to_main_keyboard()  # Добавляем кнопку "Назад"
            )
        else:
            await callback.message.edit_text(
                f"❌ Неправильно! Правильный ответ: {correct_answer}",
                reply_markup=get_back_to_main_keyboard()  # Добавляем кнопку "Назад"
            )

        await state.clear()
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "leaderboard")
    async def show_leaderboard(callback: types.CallbackQuery):
        leaderboard = get_leaderboard()
        response = "🏆 Топ-10 игроков викторины:\n\n"
        for i, user in enumerate(leaderboard, 1):
            response += f"{i}. User {user['user_id']} — {user['score']} очков\n"
        await callback.message.edit_text(
            response or "⚠️ Пока нет лидеров.",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "stats")
    async def show_stats(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "📊 Выбери период для статистики:",
            reply_markup=get_period_keyboard()
        )
        await state.set_state(UserState.selecting_period)
        await state.update_data(context="stats")
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "tournaments")
    async def show_tournaments(callback: types.CallbackQuery):
        tournaments = get_upcoming_tournaments()
        response = "🏅 Предстоящие турниры:\n\n"
        for tournament in tournaments:
            response += f"🎮 {tournament['event_name']} ({tournament['game']})\n📅 Дата: {tournament['date']}\n🔗 {tournament['url']}\n\n"
        await callback.message.edit_text(
            response or "⚠️ Нет предстоящих турниров.",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "recommend")
    async def recommend_games(callback: types.CallbackQuery):
        preferences = get_user_preferences(callback.from_user.id)
        if not preferences:
            await callback.message.edit_text(
                "🔔 Сначала настройте предпочтения в разделе '⚙️ Настройки' -> '👀 Отслеживание'.",
                reply_markup=get_main_keyboard()
            )
            return
        recommendations = await get_game_recommendations(preferences)
        response = "⭐ Рекомендуемые игры:\n\n"
        for game in recommendations[:3]:
            response += f"🎮 {game['name']} — {game['description']}\n🔗 {game['url']}\n\n"
        await callback.message.edit_text(
            response or "⚠️ Не удалось найти рекомендации.",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "feedback")
    async def show_feedback(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "📩 **Обратная связь**\n\n"
            "Напишите ваше сообщение или предложение, и я передам его разработчику! 😊\n"
            "Пример: 'Хочу добавить новую функцию X' или 'Есть баг Y'.",
            reply_markup=get_feedback_keyboard()
        )
        await state.set_state(UserState.selecting_feedback)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "back_to_main")
    async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🌟 Вы вернулись в главное меню!",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        await callback.answer()

    async def get_game_recommendations(preferences):
        if "recommendations" in cache:
            return cache["recommendations"]

        async with aiohttp.ClientSession() as session:
            url = f"http://api.steampowered.com/ISteamApps/GetAppList/v2/?key={STEAM_API_KEY}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    apps = data.get("applist", {}).get("apps", [])
                    recommendations = []
                    for app in apps:
                        appid = app["appid"]
                        name = app["name"]
                        if appid in GAMES.values() and name not in preferences:
                            recommendations.append({
                                "name": name,
                                "description": "Популярная игра на Steam!",
                                "url": f"https://store.steampowered.com/app/{appid}"
                            })
                    cache["recommendations"] = recommendations[:5]
                    return recommendations
        return []

    @dp.message(lambda message: message.text)
    async def handle_feedback(message: types.Message, state: FSMContext, bot: Bot):
        current_state = await state.get_state()
        data = await state.get_data()
        message_id = data.get("message_id")

        if current_state == UserState.selecting_feedback.state and message_id:
            feedback_text = message.text
            user_id = message.from_user.id
            user_name = message.from_user.first_name or "Аноним"
            try:
                # Edit the main message to confirm feedback submission
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message_id,
                    text=f"📩 Спасибо за вашу обратную связь! Ваше сообщение: '{feedback_text}' отправлено разработчику.\n"
                         "🌟 Вы вернулись в главное меню!",
                    reply_markup=get_main_keyboard()
                )
                # Send feedback to developer
                await bot.send_message(
                    chat_id=DEVELOPER_CHAT_ID,
                    text=f"🔔 Новая обратная связь от пользователя {user_name} (ID: {user_id}):\n\n{feedback_text}"
                )
            except Exception as e:
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message_id,
                    text="⚠️ Произошла ошибка при отправке обратной связи.",
                    reply_markup=get_main_keyboard()
                )
            await state.clear()
        else:
            # Игнорируем все текстовые сообщения, кроме тех, что в состоянии обратной связи
            await message.answer(
                "🤔 Я понимаю только команды и кнопки. Используй /start, чтобы начать, или /help, чтобы узнать, что я умею!"
            )

if __name__ == "__main__":
    from aiogram import Bot
    from config import TELEGRAM_TOKEN

    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    register_handlers(dp)

    # Добавление тестовых данных
    add_quiz_question(
        "Новая карта Basalt добавлена в игру.",
        ["CS:GO", "Rust", "Dota 2"],
        "CS:GO"
    )
    add_quiz_question(
        "Добавлены siege weapons и shields.",
        ["CS:GO", "Rust", "Team Fortress 2"],
        "Rust"
    )
    add_quiz_question(
        "Обновление 7.38b для этой игры включает фиксы для героев.",
        ["CS:GO", "Dota 2", "PUBG"],
        "Dota 2"
    )
    add_tournament(
        "CS:GO Major 2025",
        "CS:GO",
        datetime(2025, 3, 15),
        "https://www.hltv.org/events/1234/csgo-major-2025"
    )
    add_tournament(
        "The International 2025",
        "Dota 2",
        datetime(2025, 7, 1),
        "https://www.dota2.com/international"
    )

    # Запуск бота в тестовом режиме
    asyncio.run(dp.start_polling(bot))