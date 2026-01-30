"""
Database handler using SQLite
Lightweight replacement for MongoDB with file-based storage
"""
import sqlite3
import json
import asyncio
from typing import Optional, Dict, List, Any
from logger import LOGGER
from functools import wraps

def async_db_operation(func):
    """Decorator to run sync database operations in executor"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper

class Database:
    def __init__(self, db_path: str = "telegram_bot.db"):
        self.db_path = db_path
        self._init_db()
        LOGGER.info(f"SQLite Database initialized at {db_path}")
        
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        try:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    warned_count INTEGER DEFAULT 0
                )
            """)
            
            # Chats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    chat_id INTEGER PRIMARY KEY,
                    chat_title TEXT,
                    antiflood BOOLEAN DEFAULT 0,
                    welcome_enabled BOOLEAN DEFAULT 1,
                    rules TEXT
                )
            """)
            
            # Warnings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    user_id INTEGER,
                    count INTEGER DEFAULT 0,
                    UNIQUE(chat_id, user_id)
                )
            """)
            
            # Create index for warnings
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_warnings_chat_user 
                ON warnings(chat_id, user_id)
            """)
            
            # Notes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    note_name TEXT,
                    content TEXT,
                    UNIQUE(chat_id, note_name)
                )
            """)
            
            # Create index for notes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notes_chat 
                ON notes(chat_id)
            """)
            
            # AFK table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS afk (
                    user_id INTEGER PRIMARY KEY,
                    reason TEXT,
                    afk BOOLEAN DEFAULT 1
                )
            """)
            
            # Welcomes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS welcomes (
                    chat_id INTEGER PRIMARY KEY,
                    welcome_text TEXT,
                    goodbye_text TEXT,
                    photo TEXT,
                    welcome_enabled BOOLEAN DEFAULT 1,
                    goodbye_enabled BOOLEAN DEFAULT 0
                )
            """)
            
            # Migration: Add new columns if they don't exist
            try:
                cursor.execute("ALTER TABLE welcomes ADD COLUMN photo TEXT")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    LOGGER.warning(f"Could not add photo column: {e}")
            
            try:
                cursor.execute("ALTER TABLE welcomes ADD COLUMN welcome_enabled BOOLEAN DEFAULT 1")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    LOGGER.warning(f"Could not add welcome_enabled column: {e}")
            
            try:
                cursor.execute("ALTER TABLE welcomes ADD COLUMN goodbye_enabled BOOLEAN DEFAULT 0")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    LOGGER.warning(f"Could not add goodbye_enabled column: {e}")
            
            # Blacklist table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blacklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    word TEXT,
                    UNIQUE(chat_id, word)
                )
            """)
            
            # Create index for blacklist
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_blacklist_chat 
                ON blacklist(chat_id)
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def _get_connection(self):
        """Get database connection with proper threading configuration"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    # User operations
    @async_db_operation
    def add_user(self, user_id: int, username: Optional[str] = None, first_name: Optional[str] = None):
        """Add or update user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (user_id, username, first_name, warned_count)
                VALUES (?, ?, ?, 0)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name
            """, (user_id, username, first_name))
            conn.commit()
        finally:
            conn.close()
    
    @async_db_operation
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    # Chat operations
    @async_db_operation
    def add_chat(self, chat_id: int, chat_title: str):
        """Add or update chat"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO chats (chat_id, chat_title, antiflood, welcome_enabled, rules)
                VALUES (?, ?, 0, 1, NULL)
                ON CONFLICT(chat_id) DO UPDATE SET
                    chat_title = excluded.chat_title
            """, (chat_id, chat_title))
            conn.commit()
        finally:
            conn.close()
    
    @async_db_operation
    def get_chat(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get chat information"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM chats WHERE chat_id = ?", (chat_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    @async_db_operation
    def update_chat_settings(self, chat_id: int, settings: Dict[str, Any]):
        """Update chat settings"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Whitelist of allowed column names to prevent SQL injection
            allowed_columns = {'chat_title', 'antiflood', 'welcome_enabled', 'rules'}
            
            # Build dynamic UPDATE query with validated columns
            set_clauses = []
            values = []
            for key, value in settings.items():
                if key in allowed_columns:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return  # No valid columns to update
            
            values.append(chat_id)
            query = f"UPDATE chats SET {', '.join(set_clauses)} WHERE chat_id = ?"
            cursor.execute(query, values)
            conn.commit()
        finally:
            conn.close()
    
    # Warning operations
    @async_db_operation
    def add_warning(self, chat_id: int, user_id: int):
        """Add warning to user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO warnings (chat_id, user_id, count)
                VALUES (?, ?, 1)
                ON CONFLICT(chat_id, user_id) DO UPDATE SET
                    count = count + 1
            """, (chat_id, user_id))
            conn.commit()
        finally:
            conn.close()
    
    @async_db_operation
    def get_warnings(self, chat_id: int, user_id: int) -> int:
        """Get warning count for user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT count FROM warnings WHERE chat_id = ? AND user_id = ?", 
                          (chat_id, user_id))
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            conn.close()
    
    @async_db_operation
    def reset_warnings(self, chat_id: int, user_id: int):
        """Reset warnings for user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM warnings WHERE chat_id = ? AND user_id = ?", 
                          (chat_id, user_id))
            conn.commit()
        finally:
            conn.close()
    
    # Notes operations
    @async_db_operation
    def save_note(self, chat_id: int, note_name: str, note_content: str):
        """Save a note"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO notes (chat_id, note_name, content)
                VALUES (?, ?, ?)
                ON CONFLICT(chat_id, note_name) DO UPDATE SET
                    content = excluded.content
            """, (chat_id, note_name, note_content))
            conn.commit()
        finally:
            conn.close()
    
    @async_db_operation
    def get_note(self, chat_id: int, note_name: str) -> Optional[Dict[str, Any]]:
        """Get a note"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM notes WHERE chat_id = ? AND note_name = ?", 
                          (chat_id, note_name))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    @async_db_operation
    def get_all_notes(self, chat_id: int) -> List[Dict[str, Any]]:
        """Get all notes for a chat"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM notes WHERE chat_id = ?", (chat_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    @async_db_operation
    def delete_note(self, chat_id: int, note_name: str):
        """Delete a note"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM notes WHERE chat_id = ? AND note_name = ?", 
                          (chat_id, note_name))
            conn.commit()
        finally:
            conn.close()
    
    # AFK operations
    @async_db_operation
    def set_afk(self, user_id: int, reason: Optional[str] = None):
        """Set user as AFK"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO afk (user_id, reason, afk)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id) DO UPDATE SET
                    reason = excluded.reason,
                    afk = 1
            """, (user_id, reason))
            conn.commit()
        finally:
            conn.close()
    
    @async_db_operation
    def remove_afk(self, user_id: int):
        """Remove AFK status"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM afk WHERE user_id = ?", (user_id,))
            conn.commit()
        finally:
            conn.close()
    
    @async_db_operation
    def is_afk(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Check if user is AFK"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM afk WHERE user_id = ? AND afk = 1", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    # Blacklist operations
    @async_db_operation
    def add_to_blacklist(self, chat_id: int, word: str):
        """Add word to blacklist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO blacklist (chat_id, word)
                VALUES (?, ?)
            """, (chat_id, word))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Word already in blacklist
        finally:
            conn.close()
    
    @async_db_operation
    def remove_from_blacklist(self, chat_id: int, word: str):
        """Remove word from blacklist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM blacklist WHERE chat_id = ? AND word = ?", 
                          (chat_id, word))
            conn.commit()
        finally:
            conn.close()
    
    @async_db_operation
    def get_blacklist(self, chat_id: int) -> List[str]:
        """Get all blacklisted words for a chat"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT word FROM blacklist WHERE chat_id = ?", (chat_id,))
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            conn.close()
    
    # Welcome message operations
    @async_db_operation
    def get_welcome(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get welcome message settings for a chat
        
        Returns:
            Optional[Dict]: Dictionary with keys:
                - chat_id (int): Chat ID
                - welcome_text (str|None): Welcome message text
                - goodbye_text (str|None): Goodbye message text
                - photo (str|None): Photo file ID
                - welcome_enabled (int): 1 if enabled, 0 if disabled
                - goodbye_enabled (int): 1 if enabled, 0 if disabled
            Returns None if no settings exist for this chat.
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM welcomes WHERE chat_id = ?", (chat_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    @async_db_operation
    def set_welcome(self, chat_id: int, welcome_text: str, photo: Optional[str] = None):
        """Set welcome message for a chat (does not change enabled state)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO welcomes (chat_id, welcome_text, photo)
                VALUES (?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    welcome_text = excluded.welcome_text,
                    photo = excluded.photo
            """, (chat_id, welcome_text, photo))
            conn.commit()
        finally:
            conn.close()
    
    @async_db_operation
    def set_goodbye(self, chat_id: int, goodbye_text: str):
        """Set goodbye message for a chat (does not change enabled state)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO welcomes (chat_id, goodbye_text)
                VALUES (?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    goodbye_text = excluded.goodbye_text
            """, (chat_id, goodbye_text))
            conn.commit()
        finally:
            conn.close()
    
    @async_db_operation
    def delete_welcome(self, chat_id: int):
        """Delete welcome message for a chat"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM welcomes WHERE chat_id = ?", (chat_id,))
            conn.commit()
        finally:
            conn.close()
    
    @async_db_operation
    def toggle_welcome(self, chat_id: int, enabled: bool):
        """Toggle welcome messages on/off"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO welcomes (chat_id, welcome_enabled)
                VALUES (?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    welcome_enabled = excluded.welcome_enabled
            """, (chat_id, 1 if enabled else 0))
            conn.commit()
        finally:
            conn.close()
