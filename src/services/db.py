from datetime import datetime
from typing import Tuple, List
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()

USER = os.getenv("MONGODB_USERNAME")
PWD = quote_plus(os.getenv("MONGODB_PASSWORD") or "")
DB_NAME = os.getenv("MONGODB_DB_NAME") or "telegram_bot"

def _client() -> MongoClient:
    uri = f"mongodb+srv://{USER}:{PWD}@cluster0.lujfzgz.mongodb.net/{DB_NAME}?retryWrites=true&w=majority"
    return MongoClient(uri)

def col_users():
    return _client()[DB_NAME]["users"]

def col_history():
    return _client()[DB_NAME]["message_history"]

def save_dialogue(uid: str, user_text: str, bot_text: str) -> None:
    col_history().update_one(
        {"user_id": uid},
        {"$push": {"messages": {"user": user_text, "bot": bot_text}}},
        upsert=True,
    )

def subscription_valid(uid: str) -> bool:
    data = col_users().find_one({"user_id": uid})
    return data and data.get("subscription_end_date") and data["subscription_end_date"] > datetime.utcnow()
