from pymongo import MongoClient
from config import MONGO_URI

# Подключение к MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["game_updates_bot"]
users_collection = db["users"]
updates_collection = db["updates"]
quiz_collection = db["quiz"]
tournaments_collection = db["tournaments"]

def add_user(user_id):
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id, "subscribed": True, "preferred_games": [], "score": 0})

def subscribe_user(user_id):
    """Подписывает пользователя на уведомления."""
    users_collection.update_one({"user_id": user_id}, {"$set": {"subscribed": True}})

def unsubscribe_user(user_id):
    users_collection.update_one({"user_id": user_id}, {"$set": {"subscribed": False}})

def get_subscribed_users():
    return users_collection.find({"subscribed": True})

def get_user_by_id(user_id):
    """Возвращает документ пользователя по user_id."""
    return users_collection.find_one({"user_id": user_id})

def add_update(news_id, game_name, title, contents, url, date):
    if not updates_collection.find_one({"news_id": news_id}):
        updates_collection.insert_one({
            "news_id": news_id,
            "game": game_name,
            "title": title,
            "contents": contents[:500],
            "url": url,
            "date": date
        })

def get_updates_by_period(start_date):
    return updates_collection.find({"date": {"$gte": start_date}})

# Функции для викторины
def add_quiz_question(question, options, correct_answer):
    quiz_collection.insert_one({
        "question": question,
        "options": options,
        "correct_answer": correct_answer
    })

def get_random_quiz_question():
    import random
    quiz = quiz_collection.aggregate([{"$sample": {"size": 1}}])
    return next(quiz, None)

# Функции для личных настроек
def update_user_preferences(user_id, games):
    users_collection.update_one({"user_id": user_id}, {"$set": {"preferred_games": games}})

def get_user_preferences(user_id):
    user = users_collection.find_one({"user_id": user_id})
    if user:
        return user.get("preferred_games", [])
    return []

# Функции для очков викторины
def update_user_score(user_id, score_increment):
    users_collection.update_one({"user_id": user_id}, {"$inc": {"score": score_increment}})

def get_user_score(user_id):
    user = users_collection.find_one({"user_id": user_id})
    return user.get("score", 0) if user else 0

def get_leaderboard():
    return users_collection.find().sort("score", -1).limit(10)

# Функции для статистики
def get_update_stats(start_date=None):
    pipeline = [
        {"$match": {"date": {"$gte": start_date} if start_date else {}}},
        {"$group": {"_id": "$game", "count": {"$sum": 1}}}
    ]
    return list(updates_collection.aggregate(pipeline))

# Функции для турниров
def add_tournament(event_name, game, date, url):
    tournaments_collection.insert_one({
        "event_name": event_name,
        "game": game,
        "date": date,
        "url": url
    })

def get_upcoming_tournaments():
    from datetime import datetime
    return tournaments_collection.find({"date": {"$gte": datetime.now()}})