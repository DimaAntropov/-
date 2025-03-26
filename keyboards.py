from aiogram import types
from config import GAMES

def get_main_keyboard():
    buttons = [
        [types.InlineKeyboardButton(text="🔔 Обновления", callback_data="updates")],
        [types.InlineKeyboardButton(text="🎮 Дополнительно", callback_data="additional")],
        [types.InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
        [types.InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [types.InlineKeyboardButton(text="🏆 Таблица лидеров", callback_data="leaderboard")],
        [types.InlineKeyboardButton(text="🏅 Турниры", callback_data="tournaments")],
        [types.InlineKeyboardButton(text="⭐ Рекомендации", callback_data="recommend")],
        [types.InlineKeyboardButton(text="📩 Обратная связь", callback_data="feedback")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_period_keyboard():
    buttons = [
        [types.InlineKeyboardButton(text="🕒 За день", callback_data="period_day")],
        [types.InlineKeyboardButton(text="📅 За неделю", callback_data="period_week")],
        [types.InlineKeyboardButton(text="📆 За месяц", callback_data="period_month")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_additional_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="⚔️ Экшен", url="https://store.steampowered.com/category/action/"),
            types.InlineKeyboardButton(text="🛡️ Стратегии", url="https://store.steampowered.com/category/strategy/")
        ],
        [
            types.InlineKeyboardButton(text="🗡️ RPG", url="https://store.steampowered.com/category/rpg/"),
            types.InlineKeyboardButton(text="🏎️ Гонки", url="https://store.steampowered.com/category/racing/")
        ],
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_quiz_keyboard(options):
    buttons = [[types.InlineKeyboardButton(text=option, callback_data=f"quiz_answer_{option}") for option in options]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_settings_keyboard():
    """Клавиатура для подменю настроек (Отслеживание, Уведомления)."""
    buttons = [
        [types.InlineKeyboardButton(text="👀 Отслеживание", callback_data="tracking")],
        [types.InlineKeyboardButton(text="🔔 Уведомления", callback_data="notifications")],
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_tracking_keyboard(games):
    """Клавиатура для подменю отслеживания игр."""
    buttons = []
    for game, appid in GAMES.items():
        checked = "✅" if game in games else "⬜"
        buttons.append([types.InlineKeyboardButton(text=f"{checked} {game}", callback_data=f"setting_{game}")])
    buttons.append([types.InlineKeyboardButton(text="📋 Выбрать все категории", callback_data="select_all_categories")])
    buttons.append([types.InlineKeyboardButton(text="💾 Сохранить", callback_data="save_settings")])
    buttons.append([types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_tracking")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_notifications_keyboard():
    """Клавиатура для управления уведомлениями с кнопкой 'Назад'."""
    buttons = [
        [
            types.InlineKeyboardButton(text="✅ Подписаться", callback_data="subscribe"),
            types.InlineKeyboardButton(text="❌ Отписаться", callback_data="unsubscribe")
        ],
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_settings")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_feedback_keyboard():
    """Клавиатура для обратной связи."""
    buttons = [
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_back_to_period_keyboard():
    """Клавиатура с кнопкой 'Назад' для возврата к выбору периода."""
    buttons = [
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_period")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_back_to_main_keyboard():
    """Клавиатура с кнопкой 'Назад' для возврата в главное меню."""
    buttons = [
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard