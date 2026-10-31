"""
utils/db.py — إدارة قاعدة بيانات مستخدمي البوت باستخدام SQLite
"""
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = "bot_database.db"

def get_connection():
    """الحصول على اتصال بقاعدة البيانات"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """تهيئة جداول قاعدة البيانات"""
    try:
        with get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    date_joined TEXT,
                    is_blocked INTEGER DEFAULT 0,
                    language TEXT DEFAULT 'ar'
                )
            """)
            conn.commit()
            
            # محاولة إضافة عمود اللغة في حال كانت قاعدة البيانات منشأة مسبقاً بدون هذا العمود
            try:
                conn.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ar'")
                conn.commit()
            except sqlite3.OperationalError:
                # العمود موجود بالفعل
                pass
                
            logger.info("✅ Database initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")

def add_user(user_id: int, username: str, first_name: str):
    """إضافة مستخدم جديد أو تحديث بيانات مستخدم موجود"""
    try:
        # تنظيف اليوزرنيم (إزالة @ إن وجدت)
        if username and username.startswith('@'):
            username = username[1:]
            
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with get_connection() as conn:
            # التحقق أولاً لمعرفة إذا كان موجوداً لتجنب استبدال date_joined
            cursor = conn.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            if user:
                conn.execute("""
                    UPDATE users 
                    SET username = ?, first_name = ?
                    WHERE user_id = ?
                """, (username, first_name, user_id))
            else:
                conn.execute("""
                    INSERT INTO users (user_id, username, first_name, date_joined, is_blocked)
                    VALUES (?, ?, ?, ?, 0)
                """, (user_id, username, first_name, date_str))
            conn.commit()
    except Exception as e:
        logger.error(f"❌ Error adding user {user_id}: {e}")

def is_blocked(user_id: int) -> bool:
    """التحقق مما إذا كان المستخدم محظوراً"""
    try:
        with get_connection() as conn:
            cursor = conn.execute("SELECT is_blocked FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return bool(row["is_blocked"])
            return False
    except Exception as e:
        logger.error(f"❌ Error checking block status for {user_id}: {e}")
        return False

def set_blocked(user_id: int, blocked: bool) -> bool:
    """حظر أو إلغاء حظر مستخدم"""
    try:
        val = 1 if blocked else 0
        with get_connection() as conn:
            # التحقق من وجود المستخدم أولاً
            cursor = conn.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                # إذا لم يكن مسجلاً، نسجله كحالة حظر استباقي
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute("""
                    INSERT INTO users (user_id, username, first_name, date_joined, is_blocked)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, "Unknown", "Unknown", date_str, val))
            else:
                conn.execute("UPDATE users SET is_blocked = ? WHERE user_id = ?", (val, user_id))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"❌ Error setting block status for {user_id}: {e}")
        return False

def get_user_count() -> int:
    """الحصول على العدد الإجمالي للمستخدمين"""
    try:
        with get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM users")
            return cursor.fetchone()["count"]
    except Exception as e:
        logger.error(f"❌ Error getting user count: {e}")
        return 0

def get_blocked_count() -> int:
    """الحصول على عدد المستخدمين المحظورين"""
    try:
        with get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM users WHERE is_blocked = 1")
            return cursor.fetchone()["count"]
    except Exception as e:
        logger.error(f"❌ Error getting blocked count: {e}")
        return 0

def get_all_users() -> list[int]:
    """الحصول على قائمة بجميع معرّفات (IDs) المستخدمين المسجلين وغير المحظورين للرسائل الجماعية"""
    try:
        with get_connection() as conn:
            cursor = conn.execute("SELECT user_id FROM users WHERE is_blocked = 0")
            return [row["user_id"] for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"❌ Error getting all users: {e}")
        return []

def get_user_lang(user_id: int) -> str:
    """الحصول على لغة المستخدم المحددة (الافتراضية: ar)"""
    try:
        with get_connection() as conn:
            cursor = conn.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row and row["language"]:
                return row["language"]
            return "ar"
    except Exception as e:
        logger.error(f"❌ Error getting user language for {user_id}: {e}")
        return "ar"

def set_user_lang(user_id: int, lang: str) -> bool:
    """حفظ لغة المستخدم المحددة (ar أو en)"""
    try:
        with get_connection() as conn:
            conn.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"❌ Error setting user language for {user_id}: {e}")
        return False
