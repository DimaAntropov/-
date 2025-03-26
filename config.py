# Токены и константы
TELEGRAM_TOKEN = "7540008294:AAFCR77AHQDAwFwFM2VoV8vWU_HI8R9RBtQ"  # Замените на свой токен
STEAM_API_KEY = "78A97ED62C016B43824A3F16C36B1D78"       # Замените на свой ключ Steam API
MONGO_URI = "mongodb://localhost:27017"    # Замените на свою строку MongoDB
DEVELOPER_CHAT_ID = "YOUR_DEVELOPER_CHAT_ID"  # ID чата разработчика для обратной связи (замените на свой)

# Список отслеживаемых игр (AppID из Steam)
GAMES = {
    "CS:GO": 730,
    "Dota 2": 570,
    "Team Fortress 2": 440,
    "Rust": 252490,
    "GTA V": 271590,
    "PUBG": 578080,
    "Apex Legends": 1172470
}

# Кэширование (временное, для простоты)
CACHE_TTL = 3600  # Время жизни кэша в секундах (1 час)