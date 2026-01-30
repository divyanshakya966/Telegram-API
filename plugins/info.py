"""
User information extraction commands
"""
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import PeerIdInvalid, UsernameNotOccupied
from pyrogram.enums import ChatMemberStatus
from logger import LOGGER
import time

@Client.on_message(filters.command("info"))
async def user_info(client: Client, message: Message):
    """Get detailed user information"""
    try:
        if message.reply_to_message:
            user = message.reply_to_message.from_user
        elif len(message.command) > 1:
            user_input = message.command[1]
            if user_input.startswith("@"):
                user = await client.get_users(user_input)
            else:
                user = await client.get_users(int(user_input))
        else:
            user = message.from_user
        
        # Get user photos
        photos = []
        async for photo in client.get_chat_photos(user.id, limit=1):
            photos.append(photo)
        
        # Get common chats
        try:
            common = await client.get_common_chats(user.id)
            common_count = len(common)
        except:
            common_count = "N/A"
        
        # Build info text
        info_text = f"""
👤 **User Information**

🆔 **User ID:** `{user.id}`
👤 **First Name:** {user.first_name}
"""
        if user.last_name:
            info_text += f"👥 **Last Name:** {user.last_name}\n"
        if user.username:
            info_text += f"🔗 **Username:** @{user.username}\n"
        
        info_text += f"""
📱 **Is Bot:** {'Yes' if user.is_bot else 'No'}
🔰 **Is Premium:** {'Yes' if user.is_premium else 'No'}
🚫 **Is Scam:** {'Yes' if user.is_scam else 'No'}
⚠️ **Is Fake:** {'Yes' if user.is_fake else 'No'}
✅ **Is Verified:** {'Yes' if user.is_verified else 'No'}
🌐 **Language Code:** {user.language_code or 'N/A'}
📊 **Common Chats:** {common_count}
🔗 **Permanent Link:** {user.mention}
"""
        
        if user.dc_id:
            info_text += f"🌍 **DC ID:** {user.dc_id}\n"
        
        if user.phone_number:
            info_text += f"📞 **Phone:** +{user.phone_number}\n"
        
        # Send with photo if available
        if photos:
            await message.reply_photo(
                photos[0].file_id,
                caption=info_text
            )
        else:
            await message.reply_text(info_text)
        
    except PeerIdInvalid:
        await message.reply_text("❌ Invalid user ID!")
    except UsernameNotOccupied:
        await message.reply_text("❌ Username not found!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER.error(f"Info error: {e}")

@Client.on_message(filters.command("id"))
async def get_id(client: Client, message: Message):
    """Get chat/user ID"""
    try:
        if message.reply_to_message:
            user = message.reply_to_message.from_user
            text = f"👤 **User ID:** `{user.id}`\n"
            if user.username:
                text += f"🔗 **Username:** @{user.username}\n"
            if message.reply_to_message.forward_from:
                fwd = message.reply_to_message.forward_from
                text += f"\n📤 **Forwarded From:**\n"
                text += f"🆔 **ID:** `{fwd.id}`\n"
                if fwd.username:
                    text += f"🔗 **Username:** @{fwd.username}\n"
        else:
            text = f"👤 **Your ID:** `{message.from_user.id}`\n"
        
        text += f"💬 **Chat ID:** `{message.chat.id}`\n"
        text += f"📨 **Message ID:** `{message.id}`"
        
        await message.reply_text(text)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("whois"))
async def whois(client: Client, message: Message):
    """Get comprehensive user details"""
    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        elif len(message.command) > 1:
            user_input = message.command[1]
            if user_input.startswith("@"):
                user = await client.get_users(user_input)
                user_id = user.id
            else:
                user_id = int(user_input)
        else:
            user_id = message.from_user.id
        
        user = await client.get_users(user_id)
        
        # Get photos count
        photos_count = 0
        async for _ in client.get_chat_photos(user_id):
            photos_count += 1
        
        text = f"""
🔍 **WHO IS**

🆔 **ID:** `{user.id}`
📛 **Name:** {user.first_name} {user.last_name or ''}
🔤 **Username:** @{user.username or 'None'}
🤖 **Bot:** {'Yes' if user.is_bot else 'No'}
⭐ **Premium:** {'Yes' if user.is_premium else 'No'}
✅ **Verified:** {'Yes' if user.is_verified else 'No'}
🚫 **Restricted:** {'Yes' if user.is_restricted else 'No'}
⚠️ **Scam:** {'Yes' if user.is_scam else 'No'}
🎭 **Fake:** {'Yes' if user.is_fake else 'No'}
📸 **Profile Photos:** {photos_count}
🌐 **DC:** {user.dc_id or 'N/A'}
🗣️ **Language:** {user.language_code or 'N/A'}
"""
        
        if user.status:
            status_map = {
                "online": "🟢 Online",
                "offline": "⚫ Offline",
                "recently": "🟡 Recently",
                "last_week": "🟠 Within Week",
                "last_month": "🔴 Within Month",
                "long_ago": "⚫ Long Time Ago"
            }
            # Handle both enum and string status - convert to string safely
            try:
                if hasattr(user.status, 'value'):
                    status_value = user.status.value
                elif hasattr(user.status, 'name'):
                    status_value = user.status.name.lower()
                else:
                    status_value = str(user.status).replace('UserStatus.', '').lower()
            except Exception:
                status_value = "unknown"
            
            text += f"📊 **Status:** {status_map.get(status_value, 'Unknown')}\n"
        
        await message.reply_text(text)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("chatinfo"))
async def chat_info(client: Client, message: Message):
    """Get chat information"""
    try:
        chat = message.chat
        
        text = f"""
💬 **Chat Information**

🆔 **Chat ID:** `{chat.id}`
📛 **Title:** {chat.title or 'N/A'}
🔤 **Username:** @{chat.username or 'None'}
📝 **Type:** {chat.type}
"""
        
        if chat.description:
            text += f"📄 **Description:** {chat.description}\n"
        
        # Get members count
        try:
            members_count = await client.get_chat_members_count(chat.id)
            text += f"👥 **Members:** {members_count}\n"
        except:
            pass
        
        # Get admins count
        try:
            admins = []
            async for member in client.get_chat_members(chat.id, filter="administrators"):
                admins.append(member)
            text += f"👮 **Admins:** {len(admins)}\n"
        except:
            pass
        
        if chat.dc_id:
            text += f"🌍 **DC ID:** {chat.dc_id}\n"
        
        if chat.invite_link:
            text += f"🔗 **Invite Link:** {chat.invite_link}\n"
        
        # Send with photo if available
        if chat.photo:
            photo = await client.download_media(chat.photo.big_file_id, in_memory=True)
            await message.reply_photo(photo, caption=text)
        else:
            await message.reply_text(text)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("admins"))
async def list_admins(client: Client, message: Message):
    """List all admins in the chat"""
    try:
        admins_list = []
        
        async for member in client.get_chat_members(message.chat.id, filter="administrators"):
            # Handle enum status properly
            if hasattr(member.status, 'value'):
                is_owner = member.status.value == 'owner' or member.status == ChatMemberStatus.OWNER
            else:
                is_owner = str(member.status).lower() == 'owner' or member.status == ChatMemberStatus.OWNER
            
            status_emoji = "👑" if is_owner else "👮"
            user = member.user
            name = user.first_name
            if user.username:
                admins_list.append(f"{status_emoji} {name} (@{user.username})")
            else:
                admins_list.append(f"{status_emoji} {name} (`{user.id}`)")
        
        text = f"**Admins in {message.chat.title}:**\n\n"
        text += "\n".join(admins_list)
        
        await message.reply_text(text)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("stats"))
async def chat_stats(client: Client, message: Message):
    """Get chat statistics"""
    try:
        total = await client.get_chat_members_count(message.chat.id)
        
        admins = 0
        bots = 0
        banned = 0
        
        async for member in client.get_chat_members(message.chat.id, filter="administrators"):
            admins += 1
            if member.user.is_bot:
                bots += 1
        
        try:
            async for member in client.get_chat_members(message.chat.id, filter="banned"):
                banned += 1
        except:
            banned = "N/A"
        
        text = f"""
📊 **Chat Statistics**

👥 **Total Members:** {total}
👮 **Admins:** {admins}
🤖 **Bots:** {bots}
🚫 **Banned:** {banned}
👤 **Regular Users:** {total - admins}
"""
        
        await message.reply_text(text)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")