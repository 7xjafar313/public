"""
config.py — إعدادات البوت
"""
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# ==================== إعدادات البوت ====================
# دعم توكن واحد (BOT_TOKEN) أو توكنات متعددة مفصولة بفواصل (BOT_TOKENS)
BOT_TOKENS_RAW = os.getenv("BOT_TOKENS", "").strip()
if BOT_TOKENS_RAW:
    BOT_TOKENS: list[str] = [t.strip() for t in BOT_TOKENS_RAW.split(",") if t.strip()]
    BOT_TOKEN: str = BOT_TOKENS[0]
else:
    token_single = os.getenv("BOT_TOKEN", "").strip()
    BOT_TOKENS: list[str] = [token_single] if token_single else []
    BOT_TOKEN: str = token_single

if not BOT_TOKENS or not BOT_TOKEN:
    raise ValueError("❌ لم يتم تعيين BOT_TOKEN أو BOT_TOKENS في ملف .env !")

admin_id_raw = os.getenv("ADMIN_ID", "")
ADMIN_ID: int | None = int(admin_id_raw) if admin_id_raw.strip().isdigit() else None

# ==================== إعدادات التحميل ====================
DOWNLOAD_DIR: str = os.getenv("DOWNLOAD_DIR", "downloads")
MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024

DEFAULT_VIDEO_QUALITY: str = os.getenv("DEFAULT_VIDEO_QUALITY", "best")
DEFAULT_AUDIO_QUALITY: int = int(os.getenv("DEFAULT_AUDIO_QUALITY", "192"))

# ==================== خيارات الجودة ====================
VIDEO_QUALITY_OPTIONS = {
    "2160": "4K (2160p) 🎬",
    "1440": "1440p (2K) 🎥",
    "1080": "1080p (Full HD) 📺",
    "720":  "720p (HD) 📱",
    "480":  "480p (SD) 💻",
    "360":  "360p 📉",
    "240":  "240p 📉",
    "144":  "144p (أقل جودة) 📉",
    "best": "أفضل جودة متاحة ⭐",
}

AUDIO_QUALITY_OPTIONS = {
    "320": "320 kbps (أعلى جودة) 🎵",
    "256": "256 kbps 🎵",
    "192": "192 kbps (جيد) 🎵",
    "128": "128 kbps (عادي) 🎵",
    "96":  "96 kbps (منخفض) 🎵",
}

# ==================== معلومات البوت والحقوق ====================
BOT_USERNAME = "@e0e_bot"
BOT_OWNER = "@VIP_N4"
BOT_PROGRAMMER = "جعفر"
BOT_VERSION = "1.0.0"

# ==================== رسائل البوت ====================
WELCOME_MSG = """
🤖 <b>مرحباً بك في بوت التحميل الشامل!</b>

أنا بوت قوي يستخدم <b>yt-dlp</b> لتحميل المحتوى من أكثر من <b>1000 موقع</b> 🌐

<b>المواقع المدعومة تشمل:</b>
▪️ YouTube & YouTube Music
▪️ Instagram (فيديو، صور، ريلز)
▪️ Twitter / X
▪️ TikTok
▪️ Facebook
▪️ Vimeo, Dailymotion
▪️ SoundCloud (موسيقى)
▪️ Reddit, Pinterest
▪️ Twitch (كليبات)
▪️ وأكثر من 1000 موقع آخر!

<b>كيف تستخدمني؟</b>
فقط أرسل لي <b>رابط أي فيديو أو صورة</b> مباشرةً وسأتولى الباقي! 🚀

اضغط /help للمساعدة أو استخدم الأزرار أدناه 👇

━━━━━━━━━━━━━━━━━━
🤖 البوت: {bot}
👑 المالك: {owner}
👨‍💻 المبرمج: {programmer}
━━━━━━━━━━━━━━━━━━
""".format(bot=BOT_USERNAME, owner=BOT_OWNER, programmer=BOT_PROGRAMMER)

HELP_MSG = """
📖 <b>دليل الاستخدام</b>

<b>الطريقة الأساسية:</b>
أرسل الرابط مباشرةً في المحادثة وسأعرض لك خيارات التحميل.

<b>الأوامر المتاحة:</b>
/start — الشاشة الرئيسية
/help — هذه الرسالة
/settings — إعدادات التحميل
/status — حالة البوت

<b>خيارات التحميل:</b>
🎥 <b>فيديو</b> — اختر الجودة من 144p إلى 4K
🎵 <b>صوت فقط</b> — MP3 بجودة تصل إلى 320kbps
📷 <b>صور</b> — لمواقع Instagram وغيرها
📋 <b>قائمة تشغيل</b> — كل فيديوهات قائمة YouTube
ℹ️ <b>معلومات</b> — عرض تفاصيل الميديا

<b>ملاحظات:</b>
⚠️ الحد الأقصى لحجم الملف: {max_size}MB
⚠️ بعض المواقع قد تتطلب تسجيل دخول

━━━━━━━━━━━━━━━━━━
🤖 البوت: {bot}
👑 المالك: {owner}
👨‍💻 المبرمج: {programmer}
<i>جميع الحقوق محفوظة © 2025</i>
━━━━━━━━━━━━━━━━━━
""".format(max_size=MAX_FILE_SIZE_MB, bot=BOT_USERNAME, owner=BOT_OWNER, programmer=BOT_PROGRAMMER)

ABOUT_MSG = """
ℹ️ <b>عن البوت</b>

🤖 <b>الاسم:</b> بوت التحميل الشامل
🔗 <b>اليوزر:</b> {bot}
🌐 <b>الإصدار:</b> v{version}

<b>المميزات:</b>
✅ تحميل من أكثر من 1000 موقع
✅ دعم جودات متعددة حتى 4K
✅ استخراج الصوت بصيغة MP3
✅ تحميل الصور والريلز
✅ تحميل قوائم التشغيل كاملة
✅ شريط تقدم مباشر

━━━━━━━━━━━━━━━━━━
👑 <b>المالك:</b> {owner}
👨‍💻 <b>المبرمج:</b> {programmer}
<i>جميع الحقوق محفوظة © 2025</i>
━━━━━━━━━━━━━━━━━━
""".format(bot=BOT_USERNAME, owner=BOT_OWNER, programmer=BOT_PROGRAMMER, version=BOT_VERSION)

