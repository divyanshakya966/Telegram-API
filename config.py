"""
Configuration file for the bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot credentials
    API_ID = int(os.getenv("API_ID", "12345678"))
    API_HASH = os.getenv("API_HASH", "your_api_hash")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
    
    # Database (SQLite - no configuration needed, file-based)
    DB_PATH = os.getenv("DB_PATH", "telegram_bot.db")
    
    # Owner and sudo users
    OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))
    sudo_users_str = os.getenv("SUDO_USERS", "")
    SUDO_USERS = list(map(int, sudo_users_str.split())) if sudo_users_str.strip() else []
    
    # Logging
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1001234567890"))
    
    # Anti-spam settings
    FLOOD_THRESHOLD = 5  # messages per minute
    FLOOD_BAN_TIME = 600  # seconds
    
    # Welcome message settings
    DEFAULT_WELCOME = "Welcome {mention} to {chat}!"
    
    # Commands prefix
    COMMAND_PREFIXES = ["/", "!", "."]
    
    # Rate limiting
    RATE_LIMIT_DURATION = 60  # seconds
    RATE_LIMIT_MAX_REQUESTS = 20