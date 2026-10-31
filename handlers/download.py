"""
handlers/download.py — معالج التحميل الرئيسي
"""
import os
import logging
import asyncio
import uuid
from pathlib import Path

from telegram import Update, Message
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError, BadRequest

import downloader as dl


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
            await query.message.reply_text(
                text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        else:
            raise
from config import DOWNLOAD_DIR, MAX_FILE_SIZE_MB, MAX_FILE_SIZE_BYTES, BOT_USERNAME
from keyboards import (
    media_type_keyboard,
    video_quality_keyboard,
    audio_quality_keyboard,
    playlist_keyboard,
    cancel_keyboard,
    main_menu_keyboard,
    back_main_keyboard,
)
from utils.helpers import (
    is_valid_url,
    format_size,
    format_duration,
    progress_bar,
    get_domain,
    truncate_title,
)
from handlers.settings import get_user_settings
from utils.db import get_user_lang
from utils.lang import get_text

logger = logging.getLogger(__name__)

# مخزن التحميلات الجارية لكل مستخدم
active_downloads: dict[int, bool] = {}


# ==================== بناء شريط التقدم ====================
def make_progress_hook(status_msg: Message, loop: asyncio.AbstractEventLoop):
    """إنشاء دالة تتبع تقدم التحميل"""
    last_update = [0.0]

    def hook(d):
        import time
        now = time.time()
        if now - last_update[0] < 2:  # تحديث كل ثانيتين
            return
        last_update[0] = now

        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            speed = d.get("speed", 0) or 0
            eta = d.get("eta", 0) or 0

            bar = progress_bar(downloaded, total) if total else "⏳ جاري التحميل..."
            speed_str = format_size(int(speed)) + "/s" if speed else ""
            eta_str = f"{eta}ث" if eta else ""

            text = (
                f"⬇️ <b>جاري التحميل...</b>\n\n"
                f"{bar}\n"
                f"📦 {format_size(downloaded)}"
                + (f" / {format_size(total)}" if total else "")
                + (f"\n🚀 السرعة: {speed_str}" if speed_str else "")
                + (f"\n⏱️ الوقت المتبقي: {eta_str}" if eta_str else "")
            )
            asyncio.run_coroutine_threadsafe(
                _safe_edit(status_msg, text),
                loop
            )

    return hook


async def _safe_edit(msg: Message, text: str) -> None:
    """تعديل رسالة بشكل آمن"""
    try:
        await msg.edit_text(text, parse_mode=ParseMode.HTML)
    except TelegramError:
        pass


def is_short_video(url: str) -> bool:
    """التحقق مما إذا كان الرابط هو فيديو قصير (TikTok, Instagram Reels, YouTube Shorts)"""
    url_lower = url.lower()
    
    # تيك توك
    if "tiktok.com" in url_lower:
        return True
        
    # إنستغرام ريلز
    if "instagram.com" in url_lower and ("/reel/" in url_lower or "/reels/" in url_lower):
        return True
        
    # يوتيوب شورتس
    if "youtube.com/shorts/" in url_lower or "youtu.be/shorts/" in url_lower:
        return True
        
    return False


# ==================== معالج الرسائل النصية (الروابط) ====================
async def handle_url_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الرابط المرسل من المستخدم"""
    text = update.message.text.strip()
    user_id = update.effective_user.id

    # التحقق من صحة الرابط
    if not is_valid_url(text):
        lang = get_user_lang(user_id)
        await update.message.reply_text(get_text("invalid_url", lang))
        return

    lang = get_user_lang(user_id)
    # إعلام المستخدم بجلب المعلومات
    wait_msg = await update.message.reply_text(
        get_text("fetching_info", lang, domain=get_domain(text)),
        parse_mode=ParseMode.HTML
    )

    try:
        info = await dl.get_media_info(text)
        if not info:
            await wait_msg.edit_text(get_text("fetch_error", lang))
            return

        # بناء رسالة المعلومات
        title = truncate_title(info.get("title", "بدون عنوان"), 60)
        duration = format_duration(info.get("duration"))
        uploader = info.get("uploader") or info.get("channel", "")
        view_count = info.get("view_count", 0)
        is_playlist = info.get("_type") == "playlist"

        # توليد مفتاح قصير للرابط لتجنب حد 64 بايت في أزرار تيليجرام
        url_key = str(uuid.uuid4())[:8]
        if "url_map" not in context.bot_data:
            context.bot_data["url_map"] = {}
        # تنظيف المفاتيح القديمة لمنع استهلاك الذاكرة
        if len(context.bot_data["url_map"]) > 1000:
            old_keys = list(context.bot_data["url_map"].keys())[:300]
            for ok in old_keys:
                context.bot_data["url_map"].pop(ok, None)
        context.bot_data["url_map"][url_key] = text

        # التحقق مما إذا كان الفيديو قصيراً للتحميل التلقائي الفوري (تم تعطيله بناءً على رغبة المستخدم ليسأله عن الخيارات)
        # if is_short_video(text):
        #     try:
        #         await wait_msg.delete()
        #     except Exception:
        #         pass
        #     await _do_download_video(update, context, text, quality="best", url_key=url_key)
        #     return

        if is_playlist:
            entries = info.get("entries", [])
            count = len([e for e in entries if e]) if entries else "?"
            thumbnail_url = info.get("thumbnails", [{}])[-1].get("url") if info.get("thumbnails") else None
            msg = (
                f"📋 <b>قائمة تشغيل</b>\n\n"
                f"📝 <b>الاسم:</b> {title}\n"
                f"🎬 <b>عدد الفيديوهات:</b> {count}\n"
                f"👤 <b>القناة:</b> {uploader}\n\n"
                f"<i>اختر طريقة التحميل:</i>"
            )
            try:
                await wait_msg.delete()
            except Exception:
                pass
            try:
                if thumbnail_url:
                    await update.message.reply_photo(
                        photo=thumbnail_url,
                        caption=msg,
                        parse_mode=ParseMode.HTML,
                        reply_markup=playlist_keyboard(url_key, count if isinstance(count, int) else 0)
                    )
                else:
                    raise ValueError("no thumbnail")
            except Exception:
                await update.message.reply_text(
                    msg,
                    parse_mode=ParseMode.HTML,
                    reply_markup=playlist_keyboard(url_key, count if isinstance(count, int) else 0)
                )
        else:
            views_str = f"{view_count:,}" if view_count else "—"
            like_count = info.get("like_count", 0)
            likes_str = f"{like_count:,}" if like_count else "—"
            upload_date_raw = info.get("upload_date", "")
            upload_date = f"{upload_date_raw[6:8]}/{upload_date_raw[4:6]}/{upload_date_raw[:4]}" if upload_date_raw else "—"
            thumbnail_url = info.get("thumbnail") or (
                info.get("thumbnails", [{}])[-1].get("url") if info.get("thumbnails") else None
            )

            msg = (
                f"🎬 <b>{title}</b>\n\n"
                f"⏱️ <b>المدة:</b> {duration}\n"
                f"👤 <b>الرافع:</b> {uploader or '—'}\n"
                f"👁️ <b>المشاهدات:</b> {views_str}\n"
                f"❤️ <b>الإعجابات:</b> {likes_str}\n"
                f"📅 <b>التاريخ:</b> {upload_date}\n"
                f"🌐 <b>الموقع:</b> {get_domain(text)}\n\n"
                f"<i>اختر نوع التحميل:</i>"
            )
            # حفظ الرابط في سياق المستخدم
            context.user_data["last_url"] = text

            # حذف رسالة الانتظار قبل إرسال الكارت
            try:
                await wait_msg.delete()
            except Exception:
                pass

            # محاولة إرسال الكارت كصورة مع التفاصيل
            try:
                if thumbnail_url:
                    await update.message.reply_photo(
                        photo=thumbnail_url,
                        caption=msg,
                        parse_mode=ParseMode.HTML,
                        reply_markup=media_type_keyboard(url_key)
                    )
                else:
                    raise ValueError("no thumbnail")
            except Exception:
                # الرجوع للنص العادي إذا فشل تحميل الصورة
                await update.message.reply_text(
                    msg,
                    parse_mode=ParseMode.HTML,
                    reply_markup=media_type_keyboard(url_key)
                )

    except Exception as e:
        logger.error(f"Error getting media info: {e}")
        await wait_msg.edit_text(
            "❌ حدث خطأ أثناء جلب معلومات الميديا.\n"
            f"<code>{str(e)[:200]}</code>",
            parse_mode=ParseMode.HTML
        )


# ==================== معالجات أزرار نوع الميديا ====================
async def btn_type_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """اختيار تحميل فيديو"""
    query = update.callback_query
    url_key = query.data.split("|", 1)[1]
    url = context.bot_data.get("url_map", {}).get(url_key)
    if not url:
        await query.answer("⚠️ عذراً، انتهت صلاحية هذا الرابط. يرجى إرسال الرابط مجدداً.", show_alert=True)
        return
    await query.answer()
    await safe_edit_message(
        query,
        "🎥 <b>اختر جودة الفيديو:</b>",
        reply_markup=video_quality_keyboard(url_key)
    )


async def btn_type_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """اختيار تحميل صوت"""
    query = update.callback_query
    url_key = query.data.split("|", 1)[1]
    url = context.bot_data.get("url_map", {}).get(url_key)
    if not url:
        await query.answer("⚠️ عذراً، انتهت صلاحية هذا الرابط. يرجى إرسال الرابط مجدداً.", show_alert=True)
        return
    await query.answer()
    await safe_edit_message(
        query,
        "🎵 <b>اختر جودة الصوت (MP3):</b>",
        reply_markup=audio_quality_keyboard(url_key)
    )


async def btn_type_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض معلومات تفصيلية"""
    query = update.callback_query
    url_key = query.data.split("|", 1)[1]
    url = context.bot_data.get("url_map", {}).get(url_key)
    if not url:
        await query.answer("⚠️ عذراً، انتهت صلاحية هذا الرابط. يرجى إرسال الرابط مجدداً.", show_alert=True)
        return
    await query.answer("🔍 جاري جلب المعلومات...", show_alert=False)
    
    wait_msg = await query.edit_message_text(
        "🔍 <b>جاري جلب المعلومات التفصيلية...</b>",
        parse_mode=ParseMode.HTML
    )

    try:
        info = await dl.get_media_info(url)
        if not info:
            await wait_msg.edit_text("❌ لم أتمكن من جلب المعلومات.")
            return

        title = info.get("title", "—")
        duration = format_duration(info.get("duration"))
        uploader = info.get("uploader") or info.get("channel", "—")
        view_count = info.get("view_count", 0)
        like_count = info.get("like_count", 0)
        description = (info.get("description") or "")[:300]
        
        # الصيغ المتاحة
        formats = info.get("formats", [])
        video_fmts = [f for f in formats if f.get("vcodec") != "none" and f.get("height")]
        heights = sorted(set(f.get("height") for f in video_fmts if f.get("height")), reverse=True)
        qualities_str = " | ".join(f"{h}p" for h in heights[:6]) if heights else "—"

        msg = (
            f"ℹ️ <b>معلومات الميديا</b>\n\n"
            f"📝 <b>العنوان:</b>\n{title}\n\n"
            f"⏱️ <b>المدة:</b> {duration}\n"
            f"👤 <b>الرافع:</b> {uploader}\n"
            f"👁️ <b>المشاهدات:</b> {view_count:,}\n"
            f"❤️ <b>الإعجابات:</b> {like_count:,}\n"
            f"🎬 <b>الجودات المتاحة:</b> {qualities_str}\n"
            + (f"\n📄 <b>الوصف:</b>\n<i>{description}...</i>" if description else "")
        )
        await wait_msg.edit_text(
            msg,
            parse_mode=ParseMode.HTML,
            reply_markup=media_type_keyboard(url_key)
        )
    except Exception as e:
        await wait_msg.edit_text(f"❌ خطأ: <code>{str(e)[:200]}</code>", parse_mode=ParseMode.HTML)


async def btn_back_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة لقائمة نوع الميديا"""
    query = update.callback_query
    url_key = query.data.split("|", 1)[1]
    await query.answer()
    await safe_edit_message(
        query,
        "اختر نوع التحميل:",
        reply_markup=media_type_keyboard(url_key)
    )


# ==================== معالجات التحميل الفعلي ====================
async def _do_download_video(update: Update, context: ContextTypes.DEFAULT_TYPE,
                              url: str, quality: str, url_key: str) -> None:
    """تنفيذ تحميل الفيديو وإرساله"""
    query = update.callback_query
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    loop = asyncio.get_event_loop()

    # منع التحميلات المتعددة
    if active_downloads.get(user_id):
        if query:
            await query.answer("⚠️ لديك تحميل جارٍ بالفعل!", show_alert=True)
        else:
            await update.message.reply_text("⚠️ لديك تحميل جارٍ بالفعل!")
        return

    active_downloads[user_id] = True
    lang = get_user_lang(user_id)

    if query:
        await query.answer()
        status_msg = await query.edit_message_text(
            get_text("downloading", lang),
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(lang)
        )
    else:
        status_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=get_text("downloading", lang),
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(lang)
        )

    # مجلد مؤقت خاص بهذا التحميل
    temp_dir = os.path.join(DOWNLOAD_DIR, str(uuid.uuid4()))
    filepath = None

    try:
        progress_hook = make_progress_hook(status_msg, loop)
        filepath = await dl.download_video(url, quality, temp_dir, progress_hook)

        if not filepath or not os.path.exists(filepath):
            raise FileNotFoundError("لم يتم إنشاء ملف التحميل")

        file_size = os.path.getsize(filepath)

        if file_size > MAX_FILE_SIZE_BYTES:
            # ==================== الضغط الذكي ====================
            await status_msg.edit_text(
                get_text("compressing", lang, size=format_size(file_size)),
                parse_mode=ParseMode.HTML
            )

            # حساب معدل البت المستهدف لتناسب الحجم الأقصى (مع هامش أمان 5%)
            try:
                # جلب مدة الفيديو باستخدام ffprobe
                import subprocess
                import json as _json

                ffprobe_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "ffprobe.exe"
                )
                if not os.path.exists(ffprobe_path):
                    ffprobe_path = "ffprobe"  # fallback لـ PATH

                probe_cmd = [
                    ffprobe_path, "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    filepath
                ]
                probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
                probe_data = _json.loads(probe_result.stdout)
                duration_sec = float(probe_data["format"]["duration"])

                # معدل بت مستهدف بالكيلوبت لتناسب 47MB (مع هامش 5%)
                target_size_bits = (MAX_FILE_SIZE_MB * 0.95) * 1024 * 1024 * 8
                target_bitrate_kbps = int(target_size_bits / duration_sec / 1000)
                # الحد الأدنى 200 kbps لتجنب جودة رديئة جداً
                target_bitrate_kbps = max(target_bitrate_kbps, 200)

                compressed_path = filepath.replace(".mp4", "_compressed.mp4")
                ffmpeg_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "ffmpeg.exe"
                )
                if not os.path.exists(ffmpeg_path):
                    ffmpeg_path = "ffmpeg"  # fallback لـ PATH

                compress_cmd = [
                    ffmpeg_path, "-y",
                    "-i", filepath,
                    "-c:v", "libx264",
                    "-b:v", f"{target_bitrate_kbps}k",
                    "-c:a", "aac",
                    "-b:a", "96k",
                    "-preset", "fast",
                    "-movflags", "+faststart",
                    compressed_path
                ]

                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: subprocess.run(compress_cmd, capture_output=True, timeout=300)
                )

                if os.path.exists(compressed_path):
                    compressed_size = os.path.getsize(compressed_path)

                    if compressed_size <= MAX_FILE_SIZE_BYTES:
                        # الضغط نجح — إرسال الملف المضغوط
                        await status_msg.edit_text(
                            f"📤 <b>جاري رفع الفيديو المضغوط...</b>\n"
                            f"📦 الحجم بعد الضغط: {format_size(compressed_size)}",
                            parse_mode=ParseMode.HTML
                        )
                        with open(compressed_path, "rb") as f:
                            await context.bot.send_video(
                                chat_id=chat_id,
                                video=f,
                                caption=f"✅ تم التحميل بنجاح! 🎉\n"
                                        f"🔧 تم ضغطه من {format_size(file_size)} إلى {format_size(compressed_size)}\n"
                                        f"🌐 {get_domain(url)}\n\n"
                                        f"🤖 عبر البوت: {BOT_USERNAME}",
                                supports_streaming=True,
                                write_timeout=180,
                            )
                        try:
                            os.remove(compressed_path)
                        except Exception:
                            pass
                        await status_msg.edit_text(
                            "✅ <b>تم الإرسال بنجاح!</b>",
                            parse_mode=ParseMode.HTML,
                            reply_markup=back_main_keyboard()
                        )
                        return
                    else:
                        # الضغط لم يكفِ — عرض خيارات للمستخدم
                        try:
                            os.remove(compressed_path)
                        except Exception:
                            pass
                        raise ValueError(f"الملف لا يزال كبيراً بعد الضغط ({format_size(compressed_size)})")
                else:
                    raise ValueError("فشل إنشاء الملف المضغوط")

            except Exception as compress_err:
                logger.warning(f"Smart compress failed: {compress_err}")
                await status_msg.edit_text(
                    f"⚠️ <b>الملف كبير جداً ولا يمكن ضغطه كافياً!</b>\n\n"
                    f"الحجم الأصلي: {format_size(file_size)}\n"
                    f"الحد الأقصى: {MAX_FILE_SIZE_MB}MB\n\n"
                    f"جرب تحميله كصوت أو باختيار جودة أقل:",
                    parse_mode=ParseMode.HTML,
                    reply_markup=media_type_keyboard(url_key)
                )
                return

        await status_msg.edit_text(
            f"📤 <b>جاري الرفع على تيليجرام...</b>\n"
            f"📦 الحجم: {format_size(file_size)}",
            parse_mode=ParseMode.HTML
        )

        with open(filepath, "rb") as f:
            await context.bot.send_video(
                chat_id=chat_id,
                video=f,
                caption=f"✅ تم التحميل بنجاح! 🎉\n🌐 {get_domain(url)}\n\n"
                        f"🤖 عبر البوت: {BOT_USERNAME}",
                supports_streaming=True,
                write_timeout=180,
            )

        await status_msg.edit_text(
            "✅ <b>تم الإرسال بنجاح!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=back_main_keyboard()
        )

    except asyncio.CancelledError:
        await status_msg.edit_text("❌ تم إلغاء التحميل.")
    except Exception as e:
        logger.error(f"Video download failed: {e}")
        await status_msg.edit_text(
            f"❌ <b>فشل التحميل!</b>\n\n"
            f"<code>{str(e)[:300]}</code>\n\n"
            f"جرب رابطاً آخر أو جودة مختلفة.",
            parse_mode=ParseMode.HTML,
            reply_markup=back_main_keyboard()
        )
    finally:
        active_downloads.pop(user_id, None)
        # حذف الملفات المؤقتة
        if filepath:
            dl.delete_file(filepath)
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


async def btn_download_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج زر تحميل الفيديو بجودة معينة"""
    query = update.callback_query
    parts = query.data.split("|")
    quality = parts[1]
    url_key = parts[2]
    url = context.bot_data.get("url_map", {}).get(url_key)
    if not url:
        await query.answer("⚠️ عذراً، انتهت صلاحية هذا الرابط. يرجى إرسال الرابط مجدداً.", show_alert=True)
        return
    await query.answer()
    await _do_download_video(update, context, url, quality, url_key)


async def _do_download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE,
                              url: str, quality: str) -> None:
    """تنفيذ تحميل الصوت وإرساله"""
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    loop = asyncio.get_event_loop()

    if active_downloads.get(user_id):
        await query.answer("⚠️ لديك تحميل جارٍ بالفعل!", show_alert=True)
        return

    active_downloads[user_id] = True
    status_msg = await query.edit_message_text(
        "🎵 <b>جاري تحميل الصوت...</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard()
    )

    temp_dir = os.path.join(DOWNLOAD_DIR, str(uuid.uuid4()))
    filepath = None

    try:
        progress_hook = make_progress_hook(status_msg, loop)
        filepath = await dl.download_audio(url, quality, temp_dir, progress_hook)

        if not filepath or not os.path.exists(filepath):
            raise FileNotFoundError("لم يتم إنشاء ملف الصوت")

        file_size = os.path.getsize(filepath)

        if file_size > MAX_FILE_SIZE_BYTES:
            await status_msg.edit_text(
                f"⚠️ الملف كبير جداً! ({format_size(file_size)})\nالحد: {MAX_FILE_SIZE_MB}MB",
                parse_mode=ParseMode.HTML,
                reply_markup=back_main_keyboard()
            )
            return

        await status_msg.edit_text(
            f"📤 جاري الرفع... ({format_size(file_size)})",
            parse_mode=ParseMode.HTML
        )

        with open(filepath, "rb") as f:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=f,
                caption=f"🎵 تم التحميل!\n🌐 {get_domain(url)}\n\n"
                        f"🤖 عبر البوت: {BOT_USERNAME}",
                write_timeout=180,
            )

        await status_msg.edit_text(
            "✅ <b>تم الإرسال بنجاح!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=back_main_keyboard()
        )

    except Exception as e:
        logger.error(f"Audio download failed: {e}")
        await status_msg.edit_text(
            f"❌ <b>فشل التحميل!</b>\n<code>{str(e)[:300]}</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=back_main_keyboard()
        )
    finally:
        active_downloads.pop(user_id, None)
        if filepath:
            dl.delete_file(filepath)
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


async def btn_download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج زر تحميل الصوت"""
    query = update.callback_query
    parts = query.data.split("|")
    quality = parts[1]
    url_key = parts[2]
    url = context.bot_data.get("url_map", {}).get(url_key)
    if not url:
        await query.answer("⚠️ عذراً، انتهت صلاحية هذا الرابط. يرجى إرسال الرابط مجدداً.", show_alert=True)
        return
    await query.answer()
    await _do_download_audio(update, context, url, quality)


async def btn_type_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تحميل الصور"""
    query = update.callback_query
    url_key = query.data.split("|", 1)[1]
    url = context.bot_data.get("url_map", {}).get(url_key)
    if not url:
        await query.answer("⚠️ عذراً، انتهت صلاحية هذا الرابط. يرجى إرسال الرابط مجدداً.", show_alert=True)
        return
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    await query.answer()

    if active_downloads.get(user_id):
        await query.answer("⚠️ لديك تحميل جارٍ بالفعل!", show_alert=True)
        return

    active_downloads[user_id] = True
    status_msg = await query.edit_message_text(
        "📷 <b>جاري تحميل الصور...</b>",
        parse_mode=ParseMode.HTML
    )

    temp_dir = os.path.join(DOWNLOAD_DIR, str(uuid.uuid4()))

    try:
        images = await dl.download_images(url, temp_dir)

        if not images:
            await status_msg.edit_text(
                "❌ لم يتم العثور على صور.\nجرب تحميله كفيديو بدلاً من ذلك.",
                reply_markup=back_main_keyboard()
            )
            return

        await status_msg.edit_text(
            f"📤 جاري رفع {len(images)} صورة...",
            parse_mode=ParseMode.HTML
        )

        sent = 0
        for img_path in images[:10]:  # حد أقصى 10 صور
            if os.path.getsize(img_path) <= MAX_FILE_SIZE_BYTES:
                with open(img_path, "rb") as f:
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=f,
                        caption=(f"📷 صورة {sent + 1}/{len(images)}" if len(images) > 1 else f"📷 {get_domain(url)}") + f"\n\n🤖 عبر البوت: {BOT_USERNAME}"
                    )
                sent += 1
            dl.delete_file(img_path)

        await status_msg.edit_text(
            f"✅ <b>تم إرسال {sent} صورة!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=back_main_keyboard()
        )

    except Exception as e:
        logger.error(f"Image download failed: {e}")
        await status_msg.edit_text(
            f"❌ فشل تحميل الصور!\n<code>{str(e)[:300]}</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=back_main_keyboard()
        )
    finally:
        active_downloads.pop(user_id, None)
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


async def btn_playlist_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تحميل كل قائمة التشغيل كفيديو"""
    query = update.callback_query
    url_key = query.data.split("|", 1)[1]
    url = context.bot_data.get("url_map", {}).get(url_key)
    if not url:
        await query.answer("⚠️ عذراً، انتهت صلاحية هذا الرابط. يرجى إرسال الرابط مجدداً.", show_alert=True)
        return
    await query.answer()
    await _do_playlist(update, context, url, as_audio=False)


async def btn_playlist_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تحميل كل قائمة التشغيل كصوت"""
    query = update.callback_query
    url_key = query.data.split("|", 1)[1]
    url = context.bot_data.get("url_map", {}).get(url_key)
    if not url:
        await query.answer("⚠️ عذراً، انتهت صلاحية هذا الرابط. يرجى إرسال الرابط مجدداً.", show_alert=True)
        return
    await query.answer()
    await _do_playlist(update, context, url, as_audio=True)


async def _do_playlist(update: Update, context: ContextTypes.DEFAULT_TYPE,
                        url: str, as_audio: bool) -> None:
    """تحميل قائمة تشغيل كاملة"""
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if active_downloads.get(user_id):
        await query.answer("⚠️ لديك تحميل جارٍ!", show_alert=True)
        return

    active_downloads[user_id] = True
    media_type = "🎵 صوت" if as_audio else "🎥 فيديو"
    status_msg = await query.edit_message_text(
        f"📋 <b>جاري تحميل قائمة التشغيل كـ {media_type}...</b>\n"
        f"⚠️ قد يستغرق هذا وقتاً طويلاً",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard()
    )

    temp_dir = os.path.join(DOWNLOAD_DIR, str(uuid.uuid4()))

    try:
        files = await dl.download_playlist(url, as_audio, temp_dir)

        sent = 0
        for i, filepath in enumerate(files):
            if not os.path.exists(filepath):
                continue
            
            file_size = os.path.getsize(filepath)
            if file_size > MAX_FILE_SIZE_BYTES:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"⚠️ تجاوز الحجم: {os.path.basename(filepath)} ({format_size(file_size)})"
                )
                dl.delete_file(filepath)
                continue

            await status_msg.edit_text(
                f"📤 جاري رفع {i+1}/{len(files)}...",
                parse_mode=ParseMode.HTML
            )

            with open(filepath, "rb") as f:
                if as_audio:
                    await context.bot.send_audio(chat_id=chat_id, audio=f, caption=f"🤖 عبر البوت: {BOT_USERNAME}")
                else:
                    await context.bot.send_video(chat_id=chat_id, video=f, caption=f"🤖 عبر البوت: {BOT_USERNAME}", supports_streaming=True)
            
            dl.delete_file(filepath)
            sent += 1

        await status_msg.edit_text(
            f"✅ <b>تم الانتهاء!</b>\nتم إرسال {sent} من {len(files)} ملف.",
            parse_mode=ParseMode.HTML,
            reply_markup=back_main_keyboard()
        )

    except Exception as e:
        logger.error(f"Playlist download failed: {e}")
        await status_msg.edit_text(
            f"❌ فشل تحميل القائمة!\n<code>{str(e)[:300]}</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=back_main_keyboard()
        )
    finally:
        active_downloads.pop(user_id, None)
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


# ==================== الأزرار من القائمة الرئيسية ====================
async def btn_menu_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await safe_edit_message(
        query,
        "🎥 <b>تحميل فيديو</b>\n\nأرسل رابط الفيديو الذي تريد تحميله:",
        reply_markup=back_main_keyboard()
    )


async def btn_menu_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await safe_edit_message(
        query,
        "🎵 <b>تحميل صوت MP3</b>\n\nأرسل رابط الفيديو أو الأغنية:",
        reply_markup=back_main_keyboard()
    )


async def btn_menu_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await safe_edit_message(
        query,
        "📷 <b>تحميل صور</b>\n\nأرسل رابط الصفحة (Instagram, Twitter, Pinterest...):",
        reply_markup=back_main_keyboard()
    )


async def btn_menu_playlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await safe_edit_message(
        query,
        "📋 <b>تحميل قائمة تشغيل</b>\n\nأرسل رابط قائمة تشغيل YouTube:",
        reply_markup=back_main_keyboard()
    )


async def btn_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إلغاء العملية الحالية"""
    query = update.callback_query
    user_id = query.from_user.id
    active_downloads.pop(user_id, None)
    await query.answer("تم الإلغاء")
    await query.edit_message_text(
        "❌ <b>تم الإلغاء.</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu_keyboard()
    )
