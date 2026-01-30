"""
Admin management commands
"""
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid, FloodWait
from pyrogram.enums import ChatMemberStatus
from database import Database
from logger import LOGGER
import asyncio
from datetime import datetime, timedelta

db = Database()

def admin_check(func):
    """Decorator to check if user is admin"""
    async def wrapper(client: Client, message: Message):
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await message.reply_text("❌ You need to be an admin to use this command!")
            return
        return await func(client, message)
    return wrapper

@Client.on_message(filters.command("ban") & filters.group)
@admin_check
async def ban_user(client: Client, message: Message):
    """Ban a user from the chat"""
    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            user_name = message.reply_to_message.from_user.first_name
        elif len(message.command) > 1:
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            user_name = user.first_name
        else:
            await message.reply_text("❌ Reply to a user or provide user ID!")
            return
        
        # Check if target is admin
        target_member = await client.get_chat_member(message.chat.id, user_id)
        if target_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await message.reply_text("❌ Cannot ban an admin!")
            return
        
        await client.ban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"🚫 Banned {user_name}!")
        LOGGER.info(f"User {user_id} banned from {message.chat.id}")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER.error(f"Ban error: {e}")

@Client.on_message(filters.command("unban") & filters.group)
@admin_check
async def unban_user(client: Client, message: Message):
    """Unban a user"""
    try:
        if len(message.command) < 2:
            await message.reply_text("❌ Provide user ID to unban!")
            return
            
        user_id = int(message.command[1])
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"✅ Unbanned user {user_id}!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("kick") & filters.group)
@admin_check
async def kick_user(client: Client, message: Message):
    """Kick a user (ban and unban)"""
    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            user_name = message.reply_to_message.from_user.first_name
        elif len(message.command) > 1:
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            user_name = user.first_name
        else:
            await message.reply_text("❌ Reply to a user or provide user ID!")
            return
        
        target_member = await client.get_chat_member(message.chat.id, user_id)
        if target_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await message.reply_text("❌ Cannot kick an admin!")
            return
        
        await client.ban_chat_member(message.chat.id, user_id)
        await asyncio.sleep(1)
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"👢 Kicked {user_name}!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("mute") & filters.group)
@admin_check
async def mute_user(client: Client, message: Message):
    """Mute a user"""
    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            user_name = message.reply_to_message.from_user.first_name
        elif len(message.command) > 1:
            user_input = message.command[1]
            try:
                # Try to get user by username or ID
                if user_input.startswith("@"):
                    user = await client.get_users(user_input)
                else:
                    user = await client.get_users(int(user_input))
                user_id = user.id
                user_name = user.first_name
            except ValueError:
                await message.reply_text("❌ Invalid user ID!")
                return
            except Exception as e:
                await message.reply_text(f"❌ User not found: {str(e)}")
                return
        else:
            await message.reply_text("❌ Reply to a user or provide user ID/username!")
            return
        
        # Parse time if provided
        mute_time = None
        if len(message.command) > 2:
            time_str = message.command[2]
            if time_str.endswith('m'):
                mute_time = datetime.now() + timedelta(minutes=int(time_str[:-1]))
            elif time_str.endswith('h'):
                mute_time = datetime.now() + timedelta(hours=int(time_str[:-1]))
            elif time_str.endswith('d'):
                mute_time = datetime.now() + timedelta(days=int(time_str[:-1]))
        
        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(),
            until_date=mute_time
        )
        
        time_msg = f" for {message.command[2]}" if mute_time else " indefinitely"
        await message.reply_text(f"🔇 Muted {user_name}{time_msg}!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("unmute") & filters.group)
@admin_check
async def unmute_user(client: Client, message: Message):
    """Unmute a user"""
    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            user_name = message.reply_to_message.from_user.first_name
        elif len(message.command) > 1:
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            user_name = user.first_name
        else:
            await message.reply_text("❌ Reply to a user or provide user ID!")
            return
        
        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )
        await message.reply_text(f"🔊 Unmuted {user_name}!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("warn") & filters.group)
@admin_check
async def warn_user(client: Client, message: Message):
    """Warn a user (3 warnings = ban)"""
    try:
        if not message.reply_to_message:
            await message.reply_text("❌ Reply to a user to warn them!")
            return
        
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.first_name
        
        await db.add_warning(message.chat.id, user_id)
        warnings = await db.get_warnings(message.chat.id, user_id)
        
        if warnings >= 3:
            await client.ban_chat_member(message.chat.id, user_id)
            await db.reset_warnings(message.chat.id, user_id)
            await message.reply_text(f"🚫 {user_name} has been banned for exceeding warning limit!")
        else:
            warn_msg = f"⚠️ {user_name} has been warned! [{warnings}/3]"
            if len(message.command) > 1:
                reason = ' '.join(message.command[1:])
                warn_msg += f"\nReason: {reason}"
            await message.reply_text(warn_msg)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("resetwarns") & filters.group)
@admin_check
async def reset_warns(client: Client, message: Message):
    """Reset warnings for a user"""
    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        elif len(message.command) > 1:
            user_id = int(message.command[1])
        else:
            await message.reply_text("❌ Reply to a user or provide user ID!")
            return
        
        await db.reset_warnings(message.chat.id, user_id)
        await message.reply_text("✅ Warnings reset!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("pin") & filters.group)
@admin_check
async def pin_message(client: Client, message: Message):
    """Pin a message"""
    try:
        if not message.reply_to_message:
            await message.reply_text("❌ Reply to a message to pin it!")
            return
        
        loud = "loud" in (message.text or "").lower()
        await client.pin_chat_message(
            message.chat.id,
            message.reply_to_message.id,
            disable_notification=not loud
        )
        await message.reply_text("📌 Message pinned!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("unpin") & filters.group)
@admin_check
async def unpin_message(client: Client, message: Message):
    """Unpin a message"""
    try:
        if message.reply_to_message:
            await client.unpin_chat_message(message.chat.id, message.reply_to_message.id)
        else:
            await client.unpin_all_chat_messages(message.chat.id)
        await message.reply_text("✅ Message(s) unpinned!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("purge") & filters.group)
@admin_check
async def purge_messages(client: Client, message: Message):
    """Delete messages in bulk"""
    try:
        if not message.reply_to_message:
            await message.reply_text("❌ Reply to a message to start purging from!")
            return
        
        msg_ids = []
        start_id = message.reply_to_message.id
        end_id = message.id
        
        for msg_id in range(start_id, end_id + 1):
            msg_ids.append(msg_id)
        
        await client.delete_messages(message.chat.id, msg_ids)
        
        purge_msg = await message.reply_text(f"🗑️ Purged {len(msg_ids)} messages!")
        await asyncio.sleep(3)
        await purge_msg.delete()
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("promote") & filters.group)
@admin_check
async def promote_user(client: Client, message: Message):
    """Promote a user to admin"""
    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            user_name = message.reply_to_message.from_user.first_name
        elif len(message.command) > 1:
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            user_name = user.first_name
        else:
            await message.reply_text("❌ Reply to a user or provide user ID!")
            return
        
        await client.promote_chat_member(
            message.chat.id,
            user_id,
            can_delete_messages=True,
            can_restrict_members=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_promote_members=False,
            can_manage_chat=True,
            can_manage_video_chats=True
        )
        await message.reply_text(f"⬆️ Promoted {user_name} to admin!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("demote") & filters.group)
@admin_check
async def demote_user(client: Client, message: Message):
    """Demote an admin"""
    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            user_name = message.reply_to_message.from_user.first_name
        elif len(message.command) > 1:
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            user_name = user.first_name
        else:
            await message.reply_text("❌ Reply to a user or provide user ID!")
            return
        
        await client.promote_chat_member(
            message.chat.id,
            user_id,
            can_delete_messages=False,
            can_restrict_members=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=False,
            can_manage_video_chats=False
        )
        await message.reply_text(f"⬇️ Demoted {user_name}!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("lock") & filters.group)
@admin_check
async def lock_chat(client: Client, message: Message):
    """Lock the chat (restrict messages)"""
    try:
        await client.set_chat_permissions(
            message.chat.id,
            ChatPermissions()
        )
        await message.reply_text("🔒 Chat locked!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("unlock") & filters.group)
@admin_check
async def unlock_chat(client: Client, message: Message):
    """Unlock the chat"""
    try:
        await client.set_chat_permissions(
            message.chat.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True
            )
        )
        await message.reply_text("🔓 Chat unlocked!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")