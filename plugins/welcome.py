"""
Welcome and goodbye messages plugin
"""
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from database import Database
from logger import LOGGER

db = Database()

def format_welcome(text, user, chat):
    """Format welcome message with variables"""
    replacements = {
        "{mention}": user.mention,
        "{first}": user.first_name,
        "{last}": user.last_name or "",
        "{username}": f"@{user.username}" if user.username else user.first_name,
        "{id}": str(user.id),
        "{chat}": chat.title,
        "{chatid}": str(chat.id),
        "{count}": "members"  # You can get actual count if needed
    }
    
    for key, value in replacements.items():
        text = text.replace(key, str(value))
    
    return text

@Client.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(client: Client, message: Message):
    """Send welcome message to new members"""
    try:
        # Get welcome message and check if enabled
        welcome_data = await db.get_welcome(message.chat.id)
        
        # Check if welcome is enabled (default to True if no settings)
        if welcome_data and not welcome_data.get("welcome_enabled", True):
            return
        
        if welcome_data and welcome_data.get("welcome_text"):
            welcome_text = welcome_data["welcome_text"]
        else:
            welcome_text = "Welcome {mention} to {chat}! 👋"
        
        # Send welcome to each new member
        for user in message.new_chat_members:
            if user.is_bot:
                continue  # Skip bots
            
            formatted_text = format_welcome(welcome_text, user, message.chat)
            
            # Ensure the formatted text is not empty
            if not formatted_text or not formatted_text.strip():
                formatted_text = f"Welcome {user.mention}!"
            
            # Send with photo if available
            if welcome_data and welcome_data.get("photo"):
                try:
                    await message.reply_photo(
                        welcome_data["photo"],
                        caption=formatted_text
                    )
                except:
                    await message.reply_text(formatted_text)
            else:
                await message.reply_text(formatted_text)
            
            # Add user to database
            await db.add_user(user.id, user.username, user.first_name)
        
    except Exception as e:
        LOGGER.error(f"Welcome error: {e}")

@Client.on_message(filters.left_chat_member & filters.group)
async def goodbye_member(client: Client, message: Message):
    """Send goodbye message when member leaves"""
    try:
        # Check if goodbye is enabled
        goodbye_data = await db.get_welcome(message.chat.id)
        
        if not goodbye_data or not goodbye_data.get("goodbye_enabled", False):
            return
        
        user = message.left_chat_member
        
        if user.is_bot:
            return
        
        goodbye_text = goodbye_data.get("goodbye_text", "Goodbye {mention}! 👋")
        formatted_text = format_welcome(goodbye_text, user, message.chat)
        
        await message.reply_text(formatted_text)
        
    except Exception as e:
        LOGGER.error(f"Goodbye error: {e}")

@Client.on_message(filters.command("setwelcome") & filters.group)
async def set_welcome(client: Client, message: Message):
    """Set custom welcome message"""
    try:
        # Check if admin
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        # Get welcome text
        if message.reply_to_message:
            welcome_text = message.reply_to_message.text or message.reply_to_message.caption
            photo_id = None
            
            if message.reply_to_message.photo:
                photo_id = message.reply_to_message.photo.file_id
        else:
            if len(message.command) < 2:
                await message.reply_text(
                    "❌ Usage: /setwelcome [text]\n\n"
                    "Or reply to a message/photo\n\n"
                    "**Variables:**\n"
                    "• {mention} - Mention user\n"
                    "• {first} - First name\n"
                    "• {last} - Last name\n"
                    "• {username} - Username\n"
                    "• {id} - User ID\n"
                    "• {chat} - Chat name\n"
                    "• {chatid} - Chat ID"
                )
                return
            
            welcome_text = " ".join(message.command[1:])
            photo_id = None
        
        # Save to database
        await db.set_welcome(message.chat.id, welcome_text, photo_id)
        
        await message.reply_text(
            f"✅ Welcome message set!\n\n"
            f"**Preview:**\n{format_welcome(welcome_text, message.from_user, message.chat)}"
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER.error(f"Set welcome error: {e}")

@Client.on_message(filters.command("setgoodbye") & filters.group)
async def set_goodbye(client: Client, message: Message):
    """Set custom goodbye message"""
    try:
        # Check if admin
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /setgoodbye [text]")
            return
        
        goodbye_text = " ".join(message.command[1:])
        
        # Save to database
        await db.set_goodbye(message.chat.id, goodbye_text)
        
        await message.reply_text(
            f"✅ Goodbye message set!\n\n"
            f"**Preview:**\n{format_welcome(goodbye_text, message.from_user, message.chat)}"
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("welcome") & filters.group)
async def toggle_welcome(client: Client, message: Message):
    """Toggle welcome messages on/off"""
    try:
        # Check if admin
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /welcome [on/off]")
            return
        
        action = message.command[1].lower()
        
        if action == "on":
            await db.toggle_welcome(message.chat.id, True)
            await message.reply_text("✅ Welcome messages enabled!")
        elif action == "off":
            await db.toggle_welcome(message.chat.id, False)
            await message.reply_text("❌ Welcome messages disabled!")
        else:
            await message.reply_text("❌ Invalid option! Use 'on' or 'off'")
    
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("getwelcome") & filters.group)
async def show_welcome_message(client: Client, message: Message):
    """Show current welcome message"""
    try:
        welcome_data = await db.get_welcome(message.chat.id)
        
        if not welcome_data or not welcome_data.get("welcome_text"):
            await message.reply_text("❌ No custom welcome message set!")
            return
        
        text = f"**Current Welcome Message:**\n\n{welcome_data['welcome_text']}"
        
        if welcome_data.get("photo"):
            await message.reply_photo(welcome_data["photo"], caption=text)
        else:
            await message.reply_text(text)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("resetwelcome") & filters.group)
async def reset_welcome(client: Client, message: Message):
    """Reset welcome message to default"""
    try:
        # Check if admin
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        await db.delete_welcome(message.chat.id)
        await message.reply_text("✅ Welcome message reset to default!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")