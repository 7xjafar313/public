"""
handlers/start.py — معالج أوامر البداية والمساعدة مع دعم اللغتين
"""
import logging
from datetime import datetime

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from keyboards import main_menu_keyboard, back_main_keyboard
from utils.lang import get_text

logger = logging.getLogger(__name__)

import utils.db as db


# ==================== مساعد تعديل الرسائل الآمن ====================
async def safe_edit_message(query, text: str, parse_mode=ParseMode.HTML, reply_markup=None):
    """
    يحاول تعديل نص الرسالة. إذا كانت الرسالة تحتوي على وسائط (صورة/فيديو)
    فلا يمكن تعديل نصها مباشرة، لذا يتم إرسال رسالة نصية جديدة بدلاً من ذلك.
    """
    try:
        await query.edit_message_text(
            text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    except BadRequest as e:
        if "no text" in str(e).lower() or "there is no" in str(e).lower():
            # الرسالة الأصلية وسائط — أرسل رسالة نصية جديدة
            await query.message.reply_text(
                text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        else:
            raise


# ==================== مزخرف فحص الحظر وتسجيل المستخدمين ====================
def check_block(func):
    """
    مزخرف للتأكد من حظر/عدم حظر المستخدم قبل تنفيذ أي عملية،
    وتسجيل/تحديث بيانات المستخدم في قاعدة البيانات تلقائياً.
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user:
            return

        # تسجيل أو تحديث بيانات المستخدم في قاعدة البيانات
        db.add_user(user.id, user.username, user.first_name)

        # التحقق مما إذا كان المستخدم محظوراً
        if db.is_blocked(user.id):
            lang = db.get_user_lang(user.id)
            blocked_msg = get_text("blocked_alert", lang)
            if update.callback_query:
                await update.callback_query.answer(blocked_msg, show_alert=True)
            else:
                await update.message.reply_text(blocked_msg)
            return

        return await func(update, context, *args, **kwargs)
    return wrapper


@check_block
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /start"""
    import os
    user = update.effective_user
    lang = db.get_user_lang(user.id)
    logger.info(f"User {user.id} ({user.first_name}) started the bot")

    welcome_text = get_text("welcome", lang)

    # مسار صورة الترحيب
    welcome_image = os.path.join(os.path.dirname(os.path.dirname(__file__)), "welcome.png")

    if os.path.exists(welcome_image):
        with open(welcome_image, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=welcome_text,
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu_keyboard(lang)
            )
    else:
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu_keyboard(lang)
        )


@check_block
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /help"""
    lang = db.get_user_lang(update.effective_user.id)
    await update.message.reply_text(
        get_text("help", lang),
        parse_mode=ParseMode.HTML,
        reply_markup=back_main_keyboard(lang)
    )


@check_block
async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /about"""
    lang = db.get_user_lang(update.effective_user.id)
    await update.message.reply_text(
        get_text("about", lang),
        parse_mode=ParseMode.HTML,
        reply_markup=back_main_keyboard(lang)
    )


@check_block
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /status"""
    import psutil
    import platform

    lang = db.get_user_lang(update.effective_user.id)

    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage(".")

        if lang == "en":
            status_msg = f"""
📊 <b>Bot Status</b>

🟢 <b>Status:</b> Running normally
🕒 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💻 <b>OS:</b> {platform.system()} {platform.release()}

<b>Resources:</b>
🔲 CPU: {cpu}%
🧠 RAM: {ram.percent}% ({ram.used // 1024**2} MB / {ram.total // 1024**2} MB)
💾 Disk: {disk.percent}% used

<b>Powered by yt-dlp 🔧</b>
"""
        else:
            status_msg = f"""
📊 <b>حالة البوت</b>

🟢 <b>الحالة:</b> يعمل بشكل طبيعي
🕒 <b>الوقت:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💻 <b>النظام:</b> {platform.system()} {platform.release()}

<b>الموارد:</b>
🔲 CPU: {cpu}%
🧠 RAM: {ram.percent}% ({ram.used // 1024**2} MB / {ram.total // 1024**2} MB)
💾 القرص: {disk.percent}% مستخدم

<b>مدعوم بـ yt-dlp 🔧</b>
"""
    except ImportError:
        status_msg = f"📊 <b>{'Bot Status' if lang == 'en' else 'حالة البوت'}</b>\n\n🟢 {'Running' if lang == 'en' else 'يعمل'}\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    await update.message.reply_text(
        status_msg,
        parse_mode=ParseMode.HTML,
        reply_markup=back_main_keyboard(lang)
    )


@check_block
async def btn_menu_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج زر المساعدة"""
    query = update.callback_query
    await query.answer()
    lang = db.get_user_lang(query.from_user.id)
    await safe_edit_message(
        query,
        get_text("help", lang),
        reply_markup=back_main_keyboard(lang)
    )


@check_block
async def btn_menu_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج زر الحالة"""
    query = update.callback_query
    await query.answer()
    lang = db.get_user_lang(query.from_user.id)

    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        if lang == "en":
            msg = f"📊 <b>Bot Status</b>\n\n🟢 Running\n🕒 {datetime.now().strftime('%H:%M:%S')}\n🔲 CPU: {cpu}%\n🧠 RAM: {ram.percent}%"
        else:
            msg = f"📊 <b>حالة البوت</b>\n\n🟢 يعمل\n🕒 {datetime.now().strftime('%H:%M:%S')}\n🔲 CPU: {cpu}%\n🧠 RAM: {ram.percent}%"
    except ImportError:
        msg = f"📊 <b>{'Bot is running' if lang == 'en' else 'البوت يعمل'}</b>\n🕒 {datetime.now().strftime('%H:%M:%S')}"

    await safe_edit_message(
        query,
        msg,
        reply_markup=back_main_keyboard(lang)
    )


@check_block
async def btn_back_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة للقائمة الرئيسية"""
    query = update.callback_query
    await query.answer()
    lang = db.get_user_lang(query.from_user.id)
    await safe_edit_message(
        query,
        get_text("welcome", lang),
        reply_markup=main_menu_keyboard(lang)
    )
