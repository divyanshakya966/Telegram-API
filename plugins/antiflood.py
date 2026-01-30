"""
Anti-flood protection plugin
"""
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from database import Database
from logger import LOGGER
from collections import defaultdict
from datetime import datetime, timedelta

db = Database()

# Store message counts: {chat_id: {user_id: [(timestamp, count)]}}
message_tracker = defaultdict(lambda: defaultdict(list))

# Flood settings
FLOOD_THRESHOLD = 5  # messages
FLOOD_TIMEFRAME = 5  # seconds
FLOOD_BAN_DURATION = 300  # 5 minutes

def check_flood(chat_id, user_id):
    """Check if user is flooding"""
    now = datetime.now()
    user_messages = message_tracker[chat_id][user_id]
    
    # Remove old messages outside timeframe
    user_messages[:] = [
        (ts, count) for ts, count in user_messages
        if now - ts < timedelta(seconds=FLOOD_TIMEFRAME)
    ]
    
    # Count recent messages
    total_messages = sum(count for _, count in user_messages)
    
    # Add current message
    user_messages.append((now, 1))
    
    return total_messages >= FLOOD_THRESHOLD

@Client.on_message(filters.group, group=10)
async def antiflood_handler(client: Client, message: Message):
    """Monitor and prevent flooding"""
    try:
        # Skip if from admin
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ["creator", "administrator"]:
            return
        
        # Check chat settings
        chat = await db.get_chat(message.chat.id)
        if not chat or not chat.get("antiflood", False):
            return
        
        # Check for flood
        if check_flood(message.chat.id, message.from_user.id):
            # Mute user
            until_date = datetime.now() + timedelta(seconds=FLOOD_BAN_DURATION)
            
            await client.restrict_chat_member(
                message.chat.id,
                message.from_user.id,
                ChatPermissions(),
                until_date=until_date
            )
            
            # Send warning
            await message.reply_text(
                f"🚫 {message.from_user.mention} has been muted for {FLOOD_BAN_DURATION // 60} minutes "
                f"for flooding!\n\n⚠️ Flooding is not allowed in this chat."
            )
            
            # Clear message tracker for this user
            message_tracker[message.chat.id][message.from_user.id].clear()
            
            LOGGER.info(f"User {message.from_user.id} muted for flooding in {message.chat.id}")
    
    except Exception as e:
        LOGGER.error(f"Antiflood error: {e}")

@Client.on_message(filters.command("antiflood") & filters.group)
async def toggle_antiflood(client: Client, message: Message):
    """Toggle anti-flood protection"""
    try:
        # Check if admin
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ["creator", "administrator"]:
            await message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /antiflood [on/off]")
            return
        
        action = message.command[1].lower()
        
        if action == "on":
            await db.update_chat_settings(message.chat.id, {"antiflood": True})
            await message.reply_text(
                "✅ Anti-flood protection enabled!\n\n"
                f"⚙️ Settings:\n"
                f"• Maximum: {FLOOD_THRESHOLD} messages\n"
                f"• Timeframe: {FLOOD_TIMEFRAME} seconds\n"
                f"• Mute duration: {FLOOD_BAN_DURATION // 60} minutes"
            )
        elif action == "off":
            await db.update_chat_settings(message.chat.id, {"antiflood": False})
            await message.reply_text("❌ Anti-flood protection disabled!")
        else:
            await message.reply_text("❌ Invalid option! Use 'on' or 'off'")
    
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER.error(f"Toggle antiflood error: {e}")

@Client.on_message(filters.command("setflood") & filters.group)
async def set_flood_settings(client: Client, message: Message):
    """Configure flood settings"""
    try:
        # Check if admin
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ["creator", "administrator"]:
            await message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        if len(message.command) < 3:
            await message.reply_text(
                "❌ Usage: /setflood [messages] [seconds]\n\n"
                "Example: /setflood 5 10"
            )
            return
        
        try:
            threshold = int(message.command[1])
            timeframe = int(message.command[2])
            
            if threshold < 2 or threshold > 20:
                await message.reply_text("❌ Threshold must be between 2 and 20!")
                return
            
            if timeframe < 1 or timeframe > 60:
                await message.reply_text("❌ Timeframe must be between 1 and 60 seconds!")
                return
            
            # Update settings (you can store these in database too)
            global FLOOD_THRESHOLD, FLOOD_TIMEFRAME
            FLOOD_THRESHOLD = threshold
            FLOOD_TIMEFRAME = timeframe
            
            await message.reply_text(
                f"✅ Flood settings updated!\n\n"
                f"📊 New Settings:\n"
                f"• Messages: {threshold}\n"
                f"• Timeframe: {timeframe} seconds"
            )
        
        except ValueError:
            await message.reply_text("❌ Invalid numbers provided!")
    
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER.error(f"Set flood error: {e}")