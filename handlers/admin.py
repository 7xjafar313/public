"""
handlers/admin.py — معالجات لوحة تحكم الأدمن والتحكم بالمستخدمين والرسائل الجماعية
"""
import logging
import psutil
import platform
import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError

from config import ADMIN_ID
from keyboards import admin_menu_keyboard, admin_back_keyboard
import utils.db as db
from handlers.download import active_downloads

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """التحقق مما إذا كان المستخدم هو الأدمن"""
    return ADMIN_ID is not None and user_id == ADMIN_ID


async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /admin"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        # تجاهل الأمر أو إرسال رسالة تنبيه للمستخدم غير المصرح له
        await update.message.reply_text("⚠️ عذراً، هذا الأمر مخصص لإدارة البوت فقط.")
        return

    # مسح أي حالة سابقة للأدمن
    context.user_data["admin_state"] = None

    await update.message.reply_text(
        "🛠️ <b>لوحة تحكم الأدمن</b>\n\n"
        "أهلاً بك في لوحة الإدارة. يرجى اختيار أحد الخيارات أدناه لإدارة البوت:",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_menu_keyboard()
    )


async def btn_admin_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """الرجوع للوحة التحكم الرئيسية"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⚠️ غير مصرح لك بذلك.", show_alert=True)
        return
    
    await query.answer()
    context.user_data["admin_state"] = None
    
    await query.edit_message_text(
        "🛠️ <b>لوحة تحكم الأدمن</b>\n\n"
        "أهلاً بك في لوحة الإدارة. يرجى اختيار أحد الخيارات أدناه لإدارة البوت:",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_menu_keyboard()
    )


async def btn_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض إحصائيات البوت والنظام التفصيلية"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⚠️ غير مصرح لك بذلك.", show_alert=True)
        return
        
    await query.answer("جاري جلب الإحصائيات...")

    try:
        # إحصائيات النظام
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage(".")
        
        # إحصائيات قاعدة البيانات
        total_users = db.get_user_count()
        blocked_users = db.get_blocked_count()
        active_dl_count = len(active_downloads)
        
        stats_msg = f"""
📊 <b>إحصائيات البوت والنظام</b>

👥 <b>المستخدمين:</b>
├ عدد المشتركين: <b>{total_users}</b> مستخدم
└ المحظورين: <b>{blocked_users}</b> مستخدم

⏳ <b>التحميلات الحالية:</b>
└ عمليات التحميل النشطة: <b>{active_dl_count}</b> عملية

💻 <b>موارد الخادم:</b>
├ النظام: <code>{platform.system()} {platform.release()}</code>
├ معالج CPU: <code>{cpu}%</code>
├ رام RAM: <code>{ram.percent}% ({ram.used // 1024**2}MB / {ram.total // 1024**2}MB)</code>
└ القرص: <code>{disk.percent}% مستخدم (المتبقي: {disk.free // 1024**3}GB)</code>

🕒 التحديث: {datetime.now().strftime('%H:%M:%S')}
"""
    except Exception as e:
        stats_msg = f"❌ حدث خطأ أثناء جلب إحصائيات الموارد: <code>{str(e)}</code>"

    await query.edit_message_text(
        stats_msg,
        parse_mode=ParseMode.HTML,
        reply_markup=admin_back_keyboard()
    )


async def btn_admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """طلب رسالة الإذاعة"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⚠️ غير مصرح لك بذلك.", show_alert=True)
        return
        
    await query.answer()
    context.user_data["admin_state"] = "WAITING_FOR_BROADCAST"
    
    await query.edit_message_text(
        "📢 <b>إرسال رسالة جماعية (إذاعة)</b>\n\n"
        "أرسل الآن الرسالة التي تريد إذاعتها لجميع المشتركين.\n"
        "يمكن أن تكون الرسالة (نص، صورة، فيديو، ملف، إلخ).\n\n"
        "إرسال /cancel للإلغاء والعودة.",
        parse_mode=ParseMode.HTML
    )


async def btn_admin_block(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """طلب آيدي المستخدم لحظره"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⚠️ غير مصرح لك بذلك.", show_alert=True)
        return
        
    await query.answer()
    context.user_data["admin_state"] = "WAITING_FOR_BLOCK"
    
    await query.edit_message_text(
        "🚫 <b>حظر مستخدم</b>\n\n"
        "يرجى إرسال <b>معرّف الرقمي (User ID)</b> للمستخدم الذي تريد حظره من استخدام البوت:\n\n"
        "إرسال /cancel للإلغاء والعودة.",
        parse_mode=ParseMode.HTML
    )


async def btn_admin_unblock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """طلب آيدي المستخدم لإلغاء حظره"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⚠️ غير مصرح لك بذلك.", show_alert=True)
        return
        
    await query.answer()
    context.user_data["admin_state"] = "WAITING_FOR_UNBLOCK"
    
    await query.edit_message_text(
        "✅ <b>إلغاء حظر مستخدم</b>\n\n"
        "يرجى إرسال <b>معرّف الرقمي (User ID)</b> للمستخدم الذي تريد إلغاء حظره:\n\n"
        "إرسال /cancel للإلغاء والعودة.",
        parse_mode=ParseMode.HTML
    )


async def btn_admin_close(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إغلاق لوحة التحكم"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⚠️ غير مصرح لك بذلك.", show_alert=True)
        return
    await query.answer("تم إغلاق لوحة التحكم")
    context.user_data["admin_state"] = None
    await query.edit_message_text("❌ <b>تم إغلاق لوحة تحكم الأدمن.</b>", parse_mode=ParseMode.HTML)


async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    معالجة الرسائل الواردة للأدمن أثناء تفعيل إحدى حالات لوحة التحكم.
    ترجع True إذا تمت معالجة الرسالة، و False إذا لم تكن هناك حالة نشطة.
    """
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return False
        
    state = context.user_data.get("admin_state")
    if not state:
        return False

    message = update.message
    text = message.text.strip() if message.text else ""

    # إلغاء العملية
    if text == "/cancel":
        context.user_data["admin_state"] = None
        await message.reply_text(
            "❌ تم إلغاء العملية والعودة للوحة الإدارة.",
            reply_markup=admin_back_keyboard()
        )
        return True

    # 1. إذاعة رسالة
    if state == "WAITING_FOR_BROADCAST":
        users = db.get_all_users()
        if not users:
            await message.reply_text(
                "⚠️ لا يوجد أي مستخدمين مسجلين في البوت لإرسال الرسالة إليهم!",
                reply_markup=admin_back_keyboard()
            )
            context.user_data["admin_state"] = None
            return True

        status_msg = await message.reply_text(
            f"⏳ جاري البدء في إذاعة الرسالة لـ <b>{len(users)}</b> مستخدم...",
            parse_mode=ParseMode.HTML
        )

        success = 0
        failed = 0
        
        # نسخ وإرسال الرسالة لكل مستخدم
        for target_id in users:
            # تخطي الأدمن نفسه في الإذاعة لتجنب تكرار الرسالة
            if target_id == ADMIN_ID:
                continue
                
            try:
                # استخدام copy_message لنسخ الرسالة بكافة أنواعها (نص، صورة، ملصق، صوت إلخ)
                await context.bot.copy_message(
                    chat_id=target_id,
                    from_chat_id=message.chat_id,
                    message_id=message.message_id
                )
                success += 1
                # تأخير بسيط لتجنب قيود تيليجرام (Flood limits)
                await asyncio.sleep(0.05)
            except TelegramError as e:
                # إذا حظر المستخدم البوت أو حذف حسابه
                failed += 1
                logger.warning(f"Failed to send broadcast to {target_id}: {e}")

        context.user_data["admin_state"] = None
        await status_msg.edit_text(
            f"📢 <b>اكتملت عملية الإذاعة بنجاح!</b>\n\n"
            f"✅ نجاح الإرسال: <b>{success}</b>\n"
            f"❌ فشل الإرسال: <b>{failed}</b>\n\n"
            f"إجمالي المستهدفين: <b>{len(users) - 1}</b> مستخدم (بدون الأدمن).",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_back_keyboard()
        )
        return True

    # 2. حظر مستخدم
    elif state == "WAITING_FOR_BLOCK":
        if not text.isdigit():
            await message.reply_text("⚠️ خطأ! يرجى إدخال المعرّف الرقمي (User ID) كأرقام فقط:")
            return True
            
        target_id = int(text)
        if target_id == ADMIN_ID:
            await message.reply_text("❌ لا يمكنك حظر نفسك!")
            context.user_data["admin_state"] = None
            return True

        success = db.set_blocked(target_id, True)
        context.user_data["admin_state"] = None
        
        if success:
            await message.reply_text(
                f"🚫 <b>تم حظر المستخدم بنجاح!</b>\n\n"
                f"الآيدي المحظور: <code>{target_id}</code>\n"
                f"لن يتمكن من استخدام البوت أو استلام رسائل بعد الآن.",
                parse_mode=ParseMode.HTML,
                reply_markup=admin_back_keyboard()
            )
        else:
            await message.reply_text("❌ حدث خطأ غير متوقع أثناء الحظر.", reply_markup=admin_back_keyboard())
        return True

    # 3. إلغاء حظر مستخدم
    elif state == "WAITING_FOR_UNBLOCK":
        if not text.isdigit():
            await message.reply_text("⚠️ خطأ! يرجى إدخال المعرّف الرقمي (User ID) كأرقام فقط:")
            return True
            
        target_id = int(text)
        success = db.set_blocked(target_id, False)
        context.user_data["admin_state"] = None
        
        if success:
            await message.reply_text(
                f"✅ <b>تم إلغاء الحظر بنجاح!</b>\n\n"
                f"الآيدي المبرأ: <code>{target_id}</code>\n"
                f"يمكنه الآن استخدام البوت بشكل طبيعي.",
                parse_mode=ParseMode.HTML,
                reply_markup=admin_back_keyboard()
            )
        else:
            await message.reply_text("❌ حدث خطأ غير متوقع أثناء إلغاء الحظر.", reply_markup=admin_back_keyboard())
        return True

    return False


async def run_ytdlp_update() -> tuple[bool, str]:
    """تحديث مكتبة yt-dlp باستخدام pip بشكل غير متزامن"""
    import sys
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        log = stdout.decode('utf-8', errors='ignore') + "\n" + stderr.decode('utf-8', errors='ignore')
        return process.returncode == 0, log
    except Exception as e:
        return False, str(e)


async def btn_admin_update_ytdlp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج زر تحديث yt-dlp يدوياً"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⚠️ غير مصرح لك بذلك.", show_alert=True)
        return
        
    await query.answer()
    
    status_msg = await query.edit_message_text(
        "⏳ <b>جاري تحديث yt-dlp لأحدث إصدار متاح...</b>\n"
        "قد تستغرق هذه العملية بضع ثوانٍ.",
        parse_mode=ParseMode.HTML
    )
    
    success, log = await run_ytdlp_update()
    
    if success:
        import yt_dlp
        import importlib
        try:
            importlib.reload(yt_dlp)
        except Exception:
            pass
        
        await status_msg.edit_text(
            f"✅ <b>تم تحديث yt-dlp بنجاح!</b>\n\n"
            f"النسخة النشطة حالياً: <code>v{yt_dlp.version.__version__}</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_back_keyboard()
        )
    else:
        await status_msg.edit_text(
            f"❌ <b>فشل التحديث!</b>\n\n"
            f"<code>{log[:300]}</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_back_keyboard()
        )


async def auto_update_ytdlp_loop(bot) -> None:
    """حلقة تكرارية لتحديث yt-dlp تلقائياً كل 24 ساعة"""
    await asyncio.sleep(10)
    while True:
        logger.info("🔄 Running scheduled auto-update for yt-dlp...")
        success, log = await run_ytdlp_update()
        if success:
            import yt_dlp
            import importlib
            try:
                importlib.reload(yt_dlp)
            except Exception:
                pass
            logger.info(f"✅ yt-dlp auto-updated successfully. Version: {yt_dlp.version.__version__}")
            if ADMIN_ID:
                try:
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text=f"🔄 <b>تحديث تلقائي:</b> تم تحديث yt-dlp بنجاح!\nالإصدار الجديد: <code>v{yt_dlp.version.__version__}</code>",
                        parse_mode=ParseMode.HTML
                    )
                except Exception:
                    pass
        else:
            logger.error(f"❌ yt-dlp auto-update failed: {log}")
            if ADMIN_ID:
                try:
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text=f"❌ <b>تحديث تلقائي:</b> فشل تحديث yt-dlp!\n<code>{log[:200]}</code>",
                        parse_mode=ParseMode.HTML
                    )
                except Exception:
                    pass
                    
        await asyncio.sleep(24 * 3600)
