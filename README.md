# 🤖 Advanced Telegram Bot

A powerful, feature-rich Telegram bot built with Python, Pyrogram, and SQLite. Includes admin tools, user info extraction, search capabilities, and much more!

## ✨ Features

### 👮 Admin & Moderation
- Ban, kick, mute users with time limits
- Warning system (3 warnings = ban)
- Bulk message purging
- Admin promotion/demotion
- Chat locking/unlocking
- Message pinning
- Anti-flood protection
- Word blacklist system

### ℹ️ User Information
- Detailed user profiles
- Common chat detection
- Admin list
- Chat statistics
- User/chat/message IDs
- DC information

### 🛠️ Utilities
- Ping & status monitoring
- Notes system (save/retrieve custom notes)
- AFK status
- Fun commands (dice, coinflip, magic 8-ball)
- Broadcast messages

### 🔍 Search Features
- Google search
- Wikipedia integration
- YouTube search
- Text translation
- Word definitions

### 🛡️ Protection
- Anti-flood system
- Blacklist words
- Welcome/goodbye messages
- Auto-moderation
- Rate limiting

### 🎯 Multi-Bot Support
- Command autocomplete in Telegram groups
- Commands work correctly with multiple bots in same group
- Registered bot commands appear in command menu with descriptions

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- No external database needed! (SQLite included with Python)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/divyanshakya966/Telegram-API.git
cd Telegram-API
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Get Telegram credentials**
- Go to https://my.telegram.org
- Create application
- Copy API_ID and API_HASH

5. **Create bot with BotFather**
- Message @BotFather on Telegram
- Use `/newbot` command
- Copy bot token

6. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

7. **Update .env file**
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
OWNER_ID=your_telegram_id
```

8. **Run the bot**
```bash
python main.py
```

The SQLite database will be automatically created on first run!

## 📋 Command List

### Admin Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `/ban` | Ban a user | `/ban` or `/ban [user_id]` |
| `/unban` | Unban a user | `/unban [user_id]` |
| `/kick` | Kick a user | `/kick` or `/kick [user_id]` |
| `/mute` | Mute a user | `/mute [time]` (e.g., 10m, 2h, 1d) |
| `/unmute` | Unmute a user | `/unmute` |
| `/warn` | Warn a user | `/warn [reason]` |
| `/resetwarns` | Reset warnings | `/resetwarns` |
| `/pin` | Pin a message | `/pin` or `/pin loud` |
| `/unpin` | Unpin message | `/unpin` |
| `/purge` | Delete messages | Reply to message |
| `/promote` | Promote to admin | `/promote` |
| `/demote` | Demote admin | `/demote` |
| `/lock` | Lock chat | `/lock` |
| `/unlock` | Unlock chat | `/unlock` |

### Info Commands
| Command | Description |
|---------|-------------|
| `/info` | Get user details |
| `/id` | Get IDs |
| `/whois` | User information |
| `/chatinfo` | Chat details |
| `/admins` | List admins |
| `/stats` | Chat statistics |

### Utility Commands
| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Show help |
| `/ping` | Check latency |
| `/status` | System status |
| `/notes` | List notes |
| `/save` | Save a note |
| `/get` | Get a note |
| `/clear` | Delete a note |
| `/afk` | Set AFK |
| `/dice` | Roll dice |
| `/coinflip` | Flip coin |
| `/ask` | Magic 8-ball |

### Search Commands
| Command | Description |
|---------|-------------|
| `/google` | Google search |
| `/wiki` | Wikipedia search |
| `/yt` | YouTube search |
| `/tr` | Translate text |
| `/define` | Define word |

### Protection Commands
| Command | Description |
|---------|-------------|
| `/antiflood` | Toggle anti-flood |
| `/setflood` | Configure flood |
| `/blacklist` | Blacklist word |
| `/welcome` | Toggle welcome |
| `/setwelcome` | Set welcome |
| `/setgoodbye` | Set goodbye |

## 🔧 Configuration

### Environment Variables

```env
# Required
API_ID=12345678
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# Database (SQLite - file-based)
DB_PATH=telegram_bot.db  # Optional, defaults to telegram_bot.db

# Admin
OWNER_ID=123456789
SUDO_USERS=123456789,987654321  # Comma-separated

# Optional
LOG_CHANNEL=-1001234567890
```

### Database

The bot uses SQLite with the following tables:
- `users` - User information
- `chats` - Chat settings
- `warnings` - Warning records
- `notes` - Saved notes
- `afk` - AFK status
- `welcomes` - Welcome messages
- `blacklist` - Blacklisted words

**Benefits of SQLite:**
- ✅ No external database server required
- ✅ File-based storage (easy backup)
- ✅ Lightweight and fast
- ✅ Zero configuration
- ✅ Included with Python

## 📂 Project Structure

```
Telegram-API/
├── main.py              # Main bot file with command registration
├── config.py           # Configuration
├── database.py         # SQLite database operations
├── logger.py           # Logging
├── requirements.txt    # Dependencies
├── .env               # Environment variables
├── .env.example       # Env template
├── README.md          # Documentation
│
└── plugins/           # Feature modules
    ├── __init__.py
    ├── admin.py       # Admin commands
    ├── info.py        # User info
    ├── utilities.py   # Utilities
    ├── antiflood.py   # Anti-flood
    ├── welcome.py     # Welcome messages
    └── search.py      # Search commands
```

## 🎯 Advanced Usage

### Welcome Message Variables

Use these in your welcome messages:
- `{mention}` - Mention user
- `{first}` - First name
- `{last}` - Last name
- `{username}` - Username
- `{id}` - User ID
- `{chat}` - Chat name
- `{chatid}` - Chat ID

Example:
```
/setwelcome Welcome {mention} to {chat}!
```

### Anti-Flood Configuration

```bash
/setflood 5 10  # 5 messages per 10 seconds
```

### Notes with Formatting

```bash
/save rules **Chat Rules:**
1. Be respectful
2. No spam
```

## 🤖 Multi-Bot Support

This bot includes special features for working in groups with multiple bots:

### Command Autocomplete
All commands are registered with Telegram's BotCommand API, which means:
- Commands appear in the `/` menu with descriptions
- Users can see what commands are available
- Autocomplete works seamlessly in groups

### No Command Conflicts
The bot handles commands correctly even when multiple bots are in the same group. Commands are properly scoped to this bot.

## 🔒 Security

- Admin checks on all moderation commands
- Owner-only broadcast command
- Sudo users for elevated access
- Input validation on all commands
- Rate limiting to prevent abuse
- Secure database connections
- Prepared SQL statements (prevents SQL injection)

## 🐛 Troubleshooting

### Bot not responding
1. Check bot token in `.env`
2. Verify bot is added to group
3. Ensure bot has admin rights (for admin commands)
4. Check logs in console output

### Database errors
1. Ensure the bot has write permissions in its directory
2. Check `telegram_bot.db` file exists and is not corrupted
3. Try deleting the database file and restarting (creates fresh database)

### Commands not working in groups
1. Make sure bot is added to the group
2. Verify bot has necessary permissions
3. Check if privacy mode is disabled in @BotFather settings
4. Ensure commands are used correctly (check command list)

### Import errors
1. Activate virtual environment
2. Run `pip install -r requirements.txt --upgrade`
3. Check Python version (3.9+ required)

## 📊 Performance

- Handles multiple groups simultaneously
- Efficient async operations
- Optimized database queries with indexes
- Memory-efficient design
- Rate limiting protection
- Suitable for small to medium deployments (up to 10,000+ users)

## 🔄 Updates

Keep the bot updated:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
python main.py
```

## 📝 Backup

To backup your bot data, simply copy the database file:
```bash
cp telegram_bot.db telegram_bot_backup.db
```

To restore:
```bash
cp telegram_bot_backup.db telegram_bot.db
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

Built with:
- [Pyrogram](https://github.com/pyrogram/pyrogram) - Telegram MTProto API Framework
- [SQLite](https://www.sqlite.org/) - Lightweight database
- [Python](https://www.python.org/) - Programming language

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the documentation
- Review the [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) if migrating from MongoDB

## ⚠️ Disclaimer

This bot is for educational purposes. Use responsibly and comply with Telegram's Terms of Service.

## 🆕 Recent Changes

### Version 2.0 - Major Update
- ✅ **Replaced MongoDB with SQLite** - No external database required
- ✅ **Removed media streaming features** - Eliminated dependency conflicts
- ✅ **Added command autocomplete** - Better UX in Telegram groups
- ✅ **Improved multi-bot support** - Works perfectly with other bots
- ✅ **Simplified setup** - Easier installation and configuration
- ✅ **Better error handling** - More robust and reliable

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for details on migrating from the old version.

---

Made with ❤️ using Python and Pyrogram
