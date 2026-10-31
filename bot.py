"""
bot.py — الملف الرئيسي لتشغيل بوت تيليجرام
مدعوم بـ yt-dlp | python-telegram-bot v21
"""
import sys
import os
import logging
from pathlib import Path

# إضافة مسار المشروع الرئيسي لـ sys.path لتفادي مشاكل الاستيراد في السيرفرات
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# حل مشكلة ترميز الحروف والرموز التعبيرية في ويندوز
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# إعداد التسجيل
logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# إنشاء مجلد التحميلات
Path("downloads").mkdir(exist_ok=True)

# استيراد الإعدادات
from config import BOT_TOKEN, BOT_TOKENS
from utils.keep_alive import start_keep_alive, register_bot

# استيراد المعالجات
from handlers.start import (
    cmd_start, cmd_help, cmd_status, cmd_about,
    btn_menu_help, btn_menu_status, btn_back_main,
)
from handlers.settings import (
    cmd_settings, btn_menu_settings,
    btn_set_video_quality, btn_set_audio_quality,
    btn_save_video_quality, btn_save_audio_quality,
    btn_set_bot_lang, btn_save_bot_lang,
)
from handlers.download import (
    handle_url_message,
    btn_type_video, btn_type_audio, btn_type_image, btn_type_info, btn_back_media,
    btn_download_video, btn_download_audio,
    btn_playlist_all, btn_playlist_audio,
    btn_menu_video, btn_menu_audio, btn_menu_image, btn_menu_playlist,
    btn_cancel,
)

# استيراد الأدوات وقاعدة البيانات
from utils.db import init_db
from handlers.admin import (
    cmd_admin, btn_admin_main, btn_admin_stats, btn_admin_broadcast,
    btn_admin_block, btn_admin_unblock, btn_admin_close,
    btn_admin_update_ytdlp, auto_update_ytdlp_loop
)

def check_block(func):
    """مزخرف للتأكد من عدم حظر المستخدم وتسجيل بياناته تلقائياً في قاعدة البيانات"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        import utils.db as db
        user = update.effective_user
        if not user:
            return
            
        # تسجيل أو تحديث بيانات المستخدم
        db.add_user(user.id, user.username, user.first_name)
        
        # التحقق من الحظر
        if db.is_blocked(user.id):
            if update.callback_query:
                await update.callback_query.answer("🚫 عذراً، تم حظر حسابك من استخدام هذا البوت!", show_alert=True)
            else:
                await update.message.reply_text("🚫 عذراً، تم حظر حسابك من استخدام هذا البوت!")
            return
            
        return await func(update, context, *args, **kwargs)
    return wrapper

async def core_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """موجّه الرسائل الرئيسي للتعامل مع رسائل الإدارة وروابط التحميل"""
    from handlers.admin import handle_admin_text, is_admin
    import utils.db as db
    from utils.rate_limiter import check_rate_limit
    
    user = update.effective_user
    if not user:
        return
        
    # تسجيل أو تحديث بيانات المستخدم في قاعدة البيانات
    db.add_user(user.id, user.username, user.first_name)
    
    # التحقق من الحظر
    if db.is_blocked(user.id):
        await update.message.reply_text("🚫 عذراً، تم حظر حسابك من استخدام هذا البوت!")
        return
        
    # 1. إذا كان الأدمن في حالة إدخال بيانات للوحة التحكم (مثل رسالة إذاعة أو آيدي حظر)
    if is_admin(user.id) and context.user_data.get("admin_state"):
        if await handle_admin_text(update, context):
            return
            
    # 2. تحقق من معدل إرسال الرسائل (Rate Limit) لمنع السبام (للأعضاء العاديين فقط)
    if not is_admin(user.id):
        if check_rate_limit(user.id, limit=3, window=5):
            await update.message.reply_text("⚠️ **الرجاء عدم إرسال الرسائل بسرعة كبيرة!**\nانتظر قليلاً ثم حاول مجدداً.")
            return

    # 3. معالجة النصوص كروابط تحميل
    if update.message and update.message.text:
        await handle_url_message(update, context)


async def post_init(application: Application) -> None:
    """وظائف يتم تشغيلها عند بدء تشغيل البوت بالكامل"""
    import asyncio
    # تشغيل مهمة تحديث yt-dlp التلقائي في الخلفية
    asyncio.create_task(auto_update_ytdlp_loop(application.bot))

    # ضبط قائمة الأوامر للبوت تلقائياً في واجهة المستخدم (Bot SEO)
    from telegram import BotCommand
    commands = [
        BotCommand("start", "الشاشة الرئيسية للبوت 🤖"),
        BotCommand("help", "دليل الاستخدام والمساعدة 📖"),
        BotCommand("settings", "إعدادات جودة التحميل ⚙️"),
        BotCommand("status", "حالة موارد البوت 📊"),
        BotCommand("about", "حول البوت والمطورين ℹ️"),
    ]
    try:
        await application.bot.set_my_commands(commands)
    except Exception as e:
        logger.warning(f"Error setting bot commands: {e}")


def create_bot_app(token: str) -> Application:
    """إنشاء وتهيئة نسخة من تطبيق البوت مع جميع المعالجات والأزرار"""
    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    # ==================== أوامر النص ====================
    app.add_handler(CommandHandler("start",    check_block(cmd_start)))
    app.add_handler(CommandHandler("help",     check_block(cmd_help)))
    app.add_handler(CommandHandler("status",   check_block(cmd_status)))
    app.add_handler(CommandHandler("settings", check_block(cmd_settings)))
    app.add_handler(CommandHandler("about",    check_block(cmd_about)))
    app.add_handler(CommandHandler("admin",    cmd_admin))

    # ==================== معالج الرسائل الرئيسي (الروابط والأدمن) ====================
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.Document.ALL) & ~filters.COMMAND,
        core_message_handler
    ))

    # ==================== أزرار لوحة تحكم الأدمن ====================
    app.add_handler(CallbackQueryHandler(btn_admin_main,      pattern="^admin_main$"))
    app.add_handler(CallbackQueryHandler(btn_admin_stats,     pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(btn_admin_broadcast, pattern="^admin_broadcast$"))
    app.add_handler(CallbackQueryHandler(btn_admin_block,     pattern="^admin_block$"))
    app.add_handler(CallbackQueryHandler(btn_admin_unblock,   pattern="^admin_unblock$"))
    app.add_handler(CallbackQueryHandler(btn_admin_update_ytdlp, pattern="^admin_update_ytdlp$"))
    app.add_handler(CallbackQueryHandler(btn_admin_close,     pattern="^admin_close$"))

    # ==================== أزرار القائمة الرئيسية ====================
    app.add_handler(CallbackQueryHandler(check_block(btn_menu_video),    pattern="^menu_video$"))
    app.add_handler(CallbackQueryHandler(check_block(btn_menu_audio),    pattern="^menu_audio$"))
    app.add_handler(CallbackQueryHandler(check_block(btn_menu_image),    pattern="^menu_image$"))
    app.add_handler(CallbackQueryHandler(check_block(btn_menu_playlist), pattern="^menu_playlist$"))
    app.add_handler(CallbackQueryHandler(check_block(btn_menu_settings), pattern="^menu_settings$"))
    app.add_handler(CallbackQueryHandler(check_block(btn_menu_help),     pattern="^menu_help$"))
    app.add_handler(CallbackQueryHandler(check_block(btn_menu_status),   pattern="^menu_status$"))
    app.add_handler(CallbackQueryHandler(check_block(btn_back_main),     pattern="^back_main$"))

    # ==================== أزرار نوع الميديا ====================
    app.add_handler(CallbackQueryHandler(check_block(btn_type_video),  pattern=r"^type_video\|"))
    app.add_handler(CallbackQueryHandler(check_block(btn_type_audio),  pattern=r"^type_audio\|"))
    app.add_handler(CallbackQueryHandler(check_block(btn_type_image),  pattern=r"^type_image\|"))
    app.add_handler(CallbackQueryHandler(check_block(btn_type_info),   pattern=r"^type_info\|"))
    app.add_handler(CallbackQueryHandler(check_block(btn_back_media),  pattern=r"^back_media\|"))

    # ==================== أزرار الجودة والتحميل ====================
    app.add_handler(CallbackQueryHandler(check_block(btn_download_video), pattern=r"^vq\|"))
    app.add_handler(CallbackQueryHandler(check_block(btn_download_audio), pattern=r"^aq\|"))

    # ==================== أزرار قائمة التشغيل ====================
    app.add_handler(CallbackQueryHandler(check_block(btn_playlist_all),   pattern=r"^pl_all\|"))
    app.add_handler(CallbackQueryHandler(check_block(btn_playlist_audio), pattern=r"^pl_audio\|"))

    # ==================== أزرار الإعدادات ====================
    app.add_handler(CallbackQueryHandler(check_block(btn_set_video_quality), pattern="^set_video_quality$"))
    app.add_handler(CallbackQueryHandler(check_block(btn_set_audio_quality), pattern="^set_audio_quality$"))
    app.add_handler(CallbackQueryHandler(check_block(btn_save_video_quality), pattern=r"^setvq\|"))
    app.add_handler(CallbackQueryHandler(check_block(btn_save_audio_quality), pattern=r"^setaq\|"))
    app.add_handler(CallbackQueryHandler(check_block(btn_set_bot_lang),       pattern="^set_bot_lang$"))
    app.add_handler(CallbackQueryHandler(check_block(btn_save_bot_lang),      pattern=r"^setlang\|"))

    # ==================== زر الإلغاء ====================
    app.add_handler(CallbackQueryHandler(check_block(btn_cancel), pattern="^cancel$"))

    return app


def start_extra_bot_processes() -> list:
    """تشغيل أي ملفات بوت إضافية محددة في متغير EXTRA_BOTS كعمليات خلفية"""
    import subprocess
    extra_bots = os.getenv("EXTRA_BOTS", "").strip()
    if not extra_bots:
        return []

    scripts = [s.strip() for s in extra_bots.split(",") if s.strip()]
    processes = []
    for script in scripts:
        if os.path.exists(script):
            logger.info(f"🚀 بدء تشغيل بوت إضافي: {script}")
            p = subprocess.Popen([sys.executable, script])
            processes.append(p)
            register_bot(f"Script: {script}")
        else:
            logger.warning(f"⚠️ ملف البوت الإضافي غير موجود: {script}")
    return processes


async def run_multi_bots(tokens: list[str]) -> None:
    """تشغيل عدة بوتات تيليجرام بالتوازي داخل نفس حلقة الأحداث (Async Event Loop)"""
    import asyncio
    import signal

    apps = [create_bot_app(token) for token in tokens]

    for idx, app in enumerate(apps, 1):
        await app.initialize()
        await app.updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
        await app.start()
        bot_label = f"Bot #{idx} (ID: {app.bot.token.split(':')[0]})"
        register_bot(bot_label)
        logger.info(f"✅ تم تشغيل {bot_label} بنجاح!")

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except (NotImplementedError, AttributeError):
            pass

    try:
        await stop_event.wait()
    finally:
        logger.info("⏹️ جاري إيقاف جميع البوتات بأمان...")
        for app in apps:
            try:
                if app.updater and app.updater.running:
                    await app.updater.stop()
                if app.running:
                    await app.stop()
                await app.shutdown()
            except Exception as e:
                logger.warning(f"Error stopping bot app: {e}")


def main() -> None:
    """نقطة بداية تشغيل البوتات وسيرفر Keep-Alive لـ Render"""
    # 1. تهيئة قاعدة البيانات
    init_db()

    # 2. تشغيل سيرفر الويب والتنشيط الذاتي (Keep-Alive / Self-Ping) الخاص بـ Render
    start_keep_alive()

    # 3. تشغيل أي ملفات بوت إضافية إن وُجدت
    start_extra_bot_processes()

    logger.info("=" * 50)
    logger.info(f"🤖 جاري تشغيل {len(BOT_TOKENS)} بوت/بوتات في نفس الوقت...")
    logger.info("=" * 50)

    # 4. تشغيل البوتات
    if len(BOT_TOKENS) > 1:
        import asyncio
        try:
            asyncio.run(run_multi_bots(BOT_TOKENS))
        except (KeyboardInterrupt, SystemExit):
            logger.info("⏹️ تم إنهاء البوتات.")
    else:
        app = create_bot_app(BOT_TOKENS[0])
        register_bot(f"Main Bot ({BOT_TOKENS[0].split(':')[0]})")
        logger.info("✅ البوت يعمل الآن! اضغط Ctrl+C لإيقافه")
        print("\n" + "=" * 50)
        print("  🤖 بوت التحميل يعمل بنجاح!")
        print("  📱 افتح تيليجرام وتحدث مع البوت")
        print("  🌐 خادم Keep-Alive نشط لمنع Render من النوم")
        print("  ⏹️  اضغط Ctrl+C لإيقاف البوت")
        print("=" * 50 + "\n")

        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )


if __name__ == "__main__":
    main()
