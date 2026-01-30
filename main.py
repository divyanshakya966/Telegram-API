"""
Advanced Telegram Bot
Main bot initialization and command handlers
"""

from pyrogram import Client, filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from config import Config
from plugins import admin, info, utilities, antiflood, welcome
from database import Database
from logger import LOGGER
import asyncio

class TelegramBot:
    def __init__(self):
        self.app = Client(
            "my_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="plugins")
        )
        self.db = Database(Config.DB_PATH)
        
    async def start(self):
        await self.app.start()
        me = await self.app.get_me()
        LOGGER.info(f"Bot Started as @{me.username}")
        
        # Register bot commands for autocomplete in groups
        await self._register_commands()
        
    async def _register_commands(self):
        """Register bot commands for Telegram autocomplete feature"""
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help message"),
            BotCommand("ping", "Check bot latency"),
            BotCommand("status", "Show system status"),
            # Admin commands
            BotCommand("ban", "Ban a user"),
            BotCommand("unban", "Unban a user"),
            BotCommand("kick", "Kick a user"),
            BotCommand("mute", "Mute a user"),
            BotCommand("unmute", "Unmute a user"),
            BotCommand("warn", "Warn a user"),
            BotCommand("resetwarns", "Reset warnings"),
            BotCommand("pin", "Pin a message"),
            BotCommand("unpin", "Unpin message"),
            BotCommand("purge", "Delete messages"),
            BotCommand("promote", "Promote to admin"),
            BotCommand("demote", "Demote admin"),
            BotCommand("lock", "Lock chat"),
            BotCommand("unlock", "Unlock chat"),
            # Info commands
            BotCommand("info", "Get user details"),
            BotCommand("id", "Get IDs"),
            BotCommand("whois", "User information"),
            BotCommand("chatinfo", "Chat details"),
            BotCommand("admins", "List admins"),
            BotCommand("stats", "Chat statistics"),
            # Utility commands
            BotCommand("notes", "List notes"),
            BotCommand("save", "Save a note"),
            BotCommand("get", "Get a note"),
            BotCommand("clear", "Delete a note"),
            BotCommand("afk", "Set AFK status"),
            BotCommand("dice", "Roll dice"),
            BotCommand("coinflip", "Flip coin"),
            BotCommand("ask", "Magic 8-ball"),
            # Search commands
            BotCommand("google", "Google search"),
            BotCommand("wiki", "Wikipedia search"),
            BotCommand("yt", "YouTube search"),
            BotCommand("tr", "Translate text"),
            BotCommand("define", "Define word"),
            # Protection commands
            BotCommand("antiflood", "Toggle anti-flood"),
            BotCommand("setflood", "Configure flood"),
            BotCommand("blacklist", "Blacklist word"),
            BotCommand("welcome", "Toggle welcome"),
            BotCommand("setwelcome", "Set welcome message"),
            BotCommand("setgoodbye", "Set goodbye message"),
        ]
        
        try:
            await self.app.set_bot_commands(commands)
            LOGGER.info("Bot commands registered for autocomplete")
        except Exception as e:
            LOGGER.warning(f"Failed to register commands (non-critical): {e}")
        
    async def stop(self):
        await self.app.stop()
        LOGGER.info("Bot Stopped")

if __name__ == "__main__":
    bot = TelegramBot()
    bot.app.run()