"""
keyboards.py — الأزرار التفاعلية للبوت
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import VIDEO_QUALITY_OPTIONS, AUDIO_QUALITY_OPTIONS, BOT_USERNAME
from utils.lang import get_text
import urllib.parse


# ==================== القائمة الرئيسية ====================
def main_menu_keyboard(lang: str = "ar") -> InlineKeyboardMarkup:
    share_text = "بوت تحميل شامل للفيديوهات والصوتيات من يوتيوب وتيك توك وإنستغرام بدقة عالية! 🚀" if lang == "ar" else "Ultimate Media Downloader Bot for YouTube, TikTok, Instagram & Facebook! 🚀"
    bot_link = f"https://t.me/{BOT_USERNAME.replace('@', '')}"
    share_url = f"https://t.me/share/url?url={urllib.parse.quote(bot_link)}&text={urllib.parse.quote(share_text)}"

    keyboard = [
        [
            InlineKeyboardButton(get_text("btn_video", lang), callback_data="menu_video"),
            InlineKeyboardButton(get_text("btn_audio", lang), callback_data="menu_audio"),
        ],
        [
            InlineKeyboardButton(get_text("btn_image", lang), callback_data="menu_image"),
            InlineKeyboardButton(get_text("btn_playlist", lang), callback_data="menu_playlist"),
        ],
        [
            InlineKeyboardButton("⚙️ Settings / الإعدادات", callback_data="menu_settings"),
            InlineKeyboardButton("❓ Help / المساعدة", callback_data="menu_help"),
        ],
        [
            InlineKeyboardButton("📊 Status / الحالة", callback_data="menu_status"),
        ],
        [
            InlineKeyboardButton("🔗 Share Bot / شارك البوت", url=share_url),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== أزرار خيارات الميديا ====================
def media_type_keyboard(url_key: str, lang: str = "ar") -> InlineKeyboardMarkup:
    """أزرار اختيار نوع التحميل بعد إرسال الرابط"""
    keyboard = [
        [
            InlineKeyboardButton(get_text("btn_video", lang), callback_data=f"type_video|{url_key}"),
            InlineKeyboardButton(get_text("btn_audio", lang), callback_data=f"type_audio|{url_key}"),
        ],
        [
            InlineKeyboardButton(get_text("btn_image", lang), callback_data=f"type_image|{url_key}"),
            InlineKeyboardButton(get_text("btn_info", lang), callback_data=f"type_info|{url_key}"),
        ],
        [
            InlineKeyboardButton(get_text("btn_playlist", lang), callback_data=f"type_playlist|{url_key}"),
        ],
        [
            InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== أزرار جودة الفيديو ====================
def video_quality_keyboard(url_key: str, lang: str = "ar") -> InlineKeyboardMarkup:
    """أزرار اختيار جودة الفيديو"""
    keyboard = []
    row = []
    items = list(VIDEO_QUALITY_OPTIONS.items())
    
    for i, (quality_id, quality_name) in enumerate(items):
        btn = InlineKeyboardButton(
            quality_name,
            callback_data=f"vq|{quality_id}|{url_key}"
        )
        row.append(btn)
        if len(row) == 2 or i == len(items) - 1:
            keyboard.append(row)
            row = []
    
    keyboard.append([InlineKeyboardButton(get_text("btn_back", lang), callback_data=f"back_media|{url_key}")])
    keyboard.append([InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="cancel")])
    return InlineKeyboardMarkup(keyboard)


# ==================== أزرار جودة الصوت ====================
def audio_quality_keyboard(url_key: str, lang: str = "ar") -> InlineKeyboardMarkup:
    """أزرار اختيار جودة الصوت"""
    keyboard = []
    for quality_id, quality_name in AUDIO_QUALITY_OPTIONS.items():
        keyboard.append([
            InlineKeyboardButton(
                quality_name,
                callback_data=f"aq|{quality_id}|{url_key}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(get_text("btn_back", lang), callback_data=f"back_media|{url_key}")])
    keyboard.append([InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="cancel")])
    return InlineKeyboardMarkup(keyboard)


# ==================== أزرار قائمة التشغيل ====================
def playlist_keyboard(url_key: str, total: int, lang: str = "ar") -> InlineKeyboardMarkup:
    """أزرار خيارات قائمة التشغيل"""
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("btn_playlist_all", lang, count=total),
                callback_data=f"pl_all|{url_key}"
            ),
        ],
        [
            InlineKeyboardButton(get_text("btn_playlist_audio", lang), callback_data=f"pl_audio|{url_key}"),
        ],
        [InlineKeyboardButton(get_text("btn_back", lang), callback_data=f"back_media|{url_key}")],
        [InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== أزرار الإعدادات ====================
def settings_keyboard(lang: str = "ar") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(get_text("btn_settings_video", lang), callback_data="set_video_quality")],
        [InlineKeyboardButton(get_text("btn_settings_audio", lang), callback_data="set_audio_quality")],
        [InlineKeyboardButton(get_text("btn_settings_lang", lang), callback_data="set_bot_lang")],
        [InlineKeyboardButton(get_text("btn_home", lang), callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def settings_video_quality_keyboard(lang: str = "ar") -> InlineKeyboardMarkup:
    keyboard = []
    for quality_id, quality_name in VIDEO_QUALITY_OPTIONS.items():
        keyboard.append([
            InlineKeyboardButton(quality_name, callback_data=f"setvq|{quality_id}")
        ])
    keyboard.append([InlineKeyboardButton(get_text("btn_back", lang), callback_data="menu_settings")])
    return InlineKeyboardMarkup(keyboard)


def settings_audio_quality_keyboard(lang: str = "ar") -> InlineKeyboardMarkup:
    keyboard = []
    for quality_id, quality_name in AUDIO_QUALITY_OPTIONS.items():
        keyboard.append([
            InlineKeyboardButton(quality_name, callback_data=f"setaq|{quality_id}")
        ])
    keyboard.append([InlineKeyboardButton(get_text("btn_back", lang), callback_data="menu_settings")])
    return InlineKeyboardMarkup(keyboard)


def settings_lang_keyboard(lang: str = "ar") -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🇸🇦 العربية", callback_data="setlang|ar"),
            InlineKeyboardButton("🇺🇸 English", callback_data="setlang|en")
        ],
        [InlineKeyboardButton(get_text("btn_back", lang), callback_data="menu_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== زر الإلغاء ====================
def cancel_keyboard(lang: str = "ar") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="cancel")]
    ])


def back_main_keyboard(lang: str = "ar") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text("btn_home", lang), callback_data="back_main")]
    ])


# ==================== أزرار لوحة تحكم الأدمن ====================
def admin_menu_keyboard() -> InlineKeyboardMarkup:
    """أزرار لوحة تحكم الأدمن الرئيسية (أدمن فقط - لا تترجم)"""
    keyboard = [
        [
            InlineKeyboardButton("📊 إحصائيات البوت", callback_data="admin_stats"),
            InlineKeyboardButton("📢 إذاعة رسالة", callback_data="admin_broadcast"),
        ],
        [
            InlineKeyboardButton("🚫 حظر مستخدم", callback_data="admin_block"),
            InlineKeyboardButton("✅ إلغاء حظر", callback_data="admin_unblock"),
        ],
        [
            InlineKeyboardButton("🔄 تحديث yt-dlp", callback_data="admin_update_ytdlp"),
            InlineKeyboardButton("❌ إغلاق اللوحة", callback_data="admin_close"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def admin_back_keyboard() -> InlineKeyboardMarkup:
    """زر الرجوع للوحة تحكم الأدمن"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع للوحة التحكم", callback_data="admin_main")]
    ])
