"""
Utility commands - ping, status, notes, filters, etc.
"""
from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from logger import LOGGER
import time
import psutil
import platform
from datetime import datetime

db = Database()

# Cache bot username to avoid repeated API calls
_bot_username = None

async def get_bot_username(client: Client) -> str:
    """Get and cache bot username"""
    global _bot_username
    if _bot_username is None:
        me = await client.get_me()
        _bot_username = me.username
    return _bot_username

@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Start command"""
    text = f"""
👋 **Hello {message.from_user.first_name}!**

I'm an advanced Telegram bot with tons of features!

📚 **Main Commands:**
• /help - Show all commands
• /info - Get user information
• /ping - Check bot latency

💼 **Admin Commands:**
• /ban, /kick, /mute - Moderation
• /warn - Warn users
• /purge - Delete messages
• /lock, /unlock - Chat permissions

📊 **Use /help to see all commands!**
"""
    await message.reply_text(text)

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Help command with all features"""
    text = """
🔧 **Bot Command List**

**👮 Admin Commands:**
• /ban - Ban a user
• /unban - Unban a user
• /kick - Kick a user
• /mute [time] - Mute user (e.g., 10m, 2h, 1d)
• /unmute - Unmute a user
• /warn - Warn a user (3 warns = ban)
• /resetwarns - Reset warnings
• /pin [loud] - Pin a message
• /unpin - Unpin message(s)
• /purge - Delete messages in bulk
• /promote - Promote to admin
• /demote - Demote admin
• /lock - Lock chat
• /unlock - Unlock chat

**ℹ️ Info Commands:**
• /info - Get user details
• /id - Get user/chat IDs
• /whois - Comprehensive user info
• /chatinfo - Get chat information
• /admins - List all admins
• /stats - Chat statistics

**🛠️ Utility Commands:**
• /ping - Check bot latency
• /status - Bot system status
• /afk [reason] - Set AFK status
• /notes - List all notes
• /save [name] [content] - Save a note
• /get [name] - Get a note
• /clear [name] - Delete a note

**🔍 Search Commands:**
• /google [query] - Google search
• /wiki [query] - Wikipedia search
• /tr [lang] [text] - Translate text

**🎮 Fun Commands:**
• /dice - Roll a dice
• /coinflip - Flip a coin
• /ask [question] - Ask magic 8ball

**🛡️ Protection:**
• /antiflood [on/off] - Anti-flood
• /blacklist [word] - Blacklist words
• /rmblacklist [word] - Remove from blacklist
• /getblacklist - Show blacklist

**📝 Welcome:**
• /setwelcome [text] - Set welcome
• /welcome [on/off] - Toggle welcome
• /getwelcome - Show current welcome
"""
    await message.reply_text(text)

@Client.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    """Check bot latency"""
    start = time.time()
    msg = await message.reply_text("🏓 Pinging...")
    end = time.time()
    latency = (end - start) * 1000
    
    await msg.edit_text(f"🏓 **Pong!**\n⚡ Latency: `{latency:.2f}ms`")

@Client.on_message(filters.command("status"))
async def status_command(client: Client, message: Message):
    """Get bot system status"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        uptime = time.time() - psutil.boot_time()
        uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime))
        
        text = f"""
📊 **System Status**

🖥️ **CPU Usage:** {cpu_percent}%
💾 **RAM Usage:** {memory.percent}%
💿 **Disk Usage:** {disk.percent}%

📈 **Memory:**
• Used: {memory.used / (1024**3):.2f} GB
• Total: {memory.total / (1024**3):.2f} GB

💽 **Disk:**
• Used: {disk.used / (1024**3):.2f} GB
• Total: {disk.total / (1024**3):.2f} GB

⏱️ **Uptime:** {uptime_str}
🖥️ **Platform:** {platform.system()} {platform.release()}
🐍 **Python:** {platform.python_version()}
"""
        
        await message.reply_text(text)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("save") & filters.group)
async def save_note(client: Client, message: Message):
    """Save a note"""
    try:
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /save [name] [content]")
            return
        
        note_name = message.command[1].lower()
        
        if message.reply_to_message:
            note_content = message.reply_to_message.text or message.reply_to_message.caption or ""
        else:
            note_content = " ".join(message.command[2:])
        
        # Strip whitespace and check if content is empty
        note_content = note_content.strip()
        if not note_content:
            await message.reply_text("❌ No content to save!")
            return
        
        await db.save_note(message.chat.id, note_name, note_content)
        await message.reply_text(f"✅ Note `{note_name}` saved!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command(["get", "note"]) & filters.group)
async def get_note(client: Client, message: Message):
    """Get a saved note"""
    try:
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /get [name]")
            return
        
        note_name = message.command[1].lower()
        note = await db.get_note(message.chat.id, note_name)
        
        if note:
            note_content = note.get("content", "").strip()
            if note_content:
                await message.reply_text(note_content)
            else:
                await message.reply_text(f"❌ Note `{note_name}` is empty!")
        else:
            await message.reply_text(f"❌ Note `{note_name}` not found!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("notes") & filters.group)
async def list_notes(client: Client, message: Message):
    """List all notes"""
    try:
        notes = await db.get_all_notes(message.chat.id)
        
        if not notes:
            await message.reply_text("📝 No notes saved in this chat!")
            return
        
        text = "📝 **Saved Notes:**\n\n"
        for note in notes:
            text += f"• `{note['note_name']}`\n"
        
        text += f"\n**Total:** {len(notes)} notes"
        await message.reply_text(text)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("clear") & filters.group)
async def clear_note(client: Client, message: Message):
    """Delete a note"""
    try:
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /clear [name]")
            return
        
        note_name = message.command[1].lower()
        await db.delete_note(message.chat.id, note_name)
        await message.reply_text(f"✅ Note `{note_name}` deleted!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("afk"))
async def set_afk(client: Client, message: Message):
    """Set AFK status"""
    try:
        reason = " ".join(message.command[1:]) if len(message.command) > 1 else None
        await db.set_afk(message.from_user.id, reason)
        
        afk_text = f"💤 {message.from_user.first_name} is now AFK"
        if reason:
            afk_text += f"\n📝 Reason: {reason}"
        
        await message.reply_text(afk_text)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.text & filters.group, group=1)
async def check_afk(client: Client, message: Message):
    """Check if mentioned user is AFK"""
    try:
        # Skip if this is the /afk command itself
        if message.text:
            bot_username = await get_bot_username(client)
            first_word = message.text.split()[0]
            if first_word in ["/afk", f"/afk@{bot_username}"]:
                return
        
        # Check if sender was AFK
        sender_afk = await db.is_afk(message.from_user.id)
        if sender_afk:
            await db.remove_afk(message.from_user.id)
            await message.reply_text(
                f"👋 Welcome back {message.from_user.first_name}! "
                f"You are no longer AFK."
            )
            return  # Exit to avoid checking reply-to AFK status
        
        # Check if replied user is AFK (only if sender wasn't AFK)
        if message.reply_to_message and message.reply_to_message.from_user:
            user_id = message.reply_to_message.from_user.id
            afk_data = await db.is_afk(user_id)
            if afk_data:
                afk_text = f"💤 {message.reply_to_message.from_user.first_name} is AFK"
                if afk_data.get("reason"):
                    afk_text += f"\n📝 Reason: {afk_data['reason']}"
                await message.reply_text(afk_text)
        
    except Exception as e:
        LOGGER.error(f"AFK check error: {e}")

@Client.on_message(filters.command("dice"))
async def roll_dice(client: Client, message: Message):
    """Roll a dice"""
    await client.send_dice(message.chat.id, "🎲")

@Client.on_message(filters.command("coinflip"))
async def flip_coin(client: Client, message: Message):
    """Flip a coin"""
    import random
    result = random.choice(["🪙 Heads!", "🪙 Tails!"])
    await message.reply_text(result)

@Client.on_message(filters.command("ask"))
async def magic_8ball(client: Client, message: Message):
    """Magic 8-ball"""
    if len(message.command) < 2:
        await message.reply_text("❌ Ask a question!")
        return
    
    import random
    responses = [
        "Yes, definitely!", "It is certain.", "Without a doubt.",
        "Most likely.", "Outlook good.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.",
        "Don't count on it.", "My reply is no.", "My sources say no.",
        "Outlook not so good.", "Very doubtful."
    ]
    
    await message.reply_text(f"🎱 {random.choice(responses)}")

@Client.on_message(filters.command("broadcast"))
async def broadcast_message(client: Client, message: Message):
    """Broadcast message to all chats (Owner only)"""
    from config import Config
    
    if message.from_user.id != Config.OWNER_ID:
        await message.reply_text("❌ This command is owner only!")
        return
    
    if not message.reply_to_message:
        await message.reply_text("❌ Reply to a message to broadcast!")
        return
    
    sent = 0
    failed = 0
    
    status_msg = await message.reply_text("📡 Broadcasting...")
    
    async for dialog in client.get_dialogs():
        try:
            await message.reply_to_message.copy(dialog.chat.id)
            sent += 1
        except:
            failed += 1
    
    await status_msg.edit_text(
        f"✅ Broadcast complete!\n"
        f"📤 Sent: {sent}\n"
        f"❌ Failed: {failed}"
    )

@Client.on_message(filters.command("blacklist") & filters.group)
async def add_blacklist(client: Client, message: Message):
    """Add word to blacklist"""
    from pyrogram.enums import ChatMemberStatus
    
    try:
        # Check if admin
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /blacklist [word]")
            return
        
        word = " ".join(message.command[1:]).lower()
        await db.add_to_blacklist(message.chat.id, word)
        await message.reply_text(f"✅ Added `{word}` to blacklist!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER.error(f"Blacklist error: {e}")

@Client.on_message(filters.command("rmblacklist") & filters.group)
async def remove_blacklist(client: Client, message: Message):
    """Remove word from blacklist"""
    from pyrogram.enums import ChatMemberStatus
    
    try:
        # Check if admin
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /rmblacklist [word]")
            return
        
        word = " ".join(message.command[1:]).lower()
        await db.remove_from_blacklist(message.chat.id, word)
        await message.reply_text(f"✅ Removed `{word}` from blacklist!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER.error(f"Remove blacklist error: {e}")

@Client.on_message(filters.command("getblacklist") & filters.group)
async def show_blacklist(client: Client, message: Message):
    """Show blacklisted words"""
    try:
        blacklist = await db.get_blacklist(message.chat.id)
        
        if not blacklist:
            await message.reply_text("📝 No words in blacklist!")
            return
        
        text = "🚫 **Blacklisted Words:**\n\n"
        for word in blacklist:
            text += f"• `{word}`\n"
        
        text += f"\n**Total:** {len(blacklist)} words"
        await message.reply_text(text)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER.error(f"Get blacklist error: {e}")

@Client.on_message((filters.text | filters.caption) & filters.group, group=2)
async def check_blacklist(client: Client, message: Message):
    """Check and delete messages with blacklisted words"""
    from pyrogram.enums import ChatMemberStatus
    import asyncio
    import re
    
    try:
        # Skip if from admin
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return
        
        # Get blacklist
        blacklist = await db.get_blacklist(message.chat.id)
        
        if not blacklist:
            return
        
        # Check if message contains blacklisted words
        message_text = (message.text or message.caption or "").lower()
        
        for word in blacklist:
            # Use word boundary matching to avoid false positives
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, message_text):
                try:
                    await message.delete()
                    warn_msg = await message.reply_text(
                        f"⚠️ {message.from_user.mention}, your message was deleted "
                        f"because it contains a blacklisted word!"
                    )
                    # Auto-delete warning after 5 seconds (non-blocking)
                    asyncio.create_task(self_delete_message(warn_msg))
                except Exception as del_err:
                    LOGGER.error(f"Error deleting blacklisted message: {del_err}")
                break
        
    except Exception as e:
        LOGGER.error(f"Blacklist check error: {e}")

async def self_delete_message(message):
    """Helper function to auto-delete message after delay"""
    import asyncio
    try:
        await asyncio.sleep(5)
        await message.delete()
    except Exception as e:
        LOGGER.error(f"Error auto-deleting message: {e}")