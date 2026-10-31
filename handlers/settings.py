"""
handlers/settings.py — معالج الإعدادات مع دعم اللغتين
"""
import logging
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from keyboards import (
    settings_keyboard,
    settings_video_quality_keyboard,
    settings_audio_quality_keyboard,
    settings_lang_keyboard,
    main_menu_keyboard,
)
from config import VIDEO_QUALITY_OPTIONS, AUDIO_QUALITY_OPTIONS
from utils.db import get_user_lang, set_user_lang
from utils.lang import get_text

logger = logging.getLogger(__name__)

# مخزن إعدادات المستخدمين (في الذاكرة)
user_settings: dict[int, dict] = {}


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


def get_user_settings(user_id: int) -> dict:
    """الحصول على إعدادات المستخدم أو القيم الافتراضية"""
    if user_id not in user_settings:
        user_settings[user_id] = {
            "video_quality": "best",
            "audio_quality": "192",
        }
    return user_settings[user_id]


async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /settings"""
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    settings = get_user_settings(user_id)
    vq = VIDEO_QUALITY_OPTIONS.get(settings["video_quality"], settings["video_quality"])
    aq = AUDIO_QUALITY_OPTIONS.get(settings["audio_quality"], settings["audio_quality"])

    msg = get_text("settings_title", lang, vq=vq, aq=aq)
    await update.message.reply_text(
        msg,
        parse_mode=ParseMode.HTML,
        reply_markup=settings_keyboard(lang)
    )


async def btn_menu_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج زر الإعدادات"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    settings = get_user_settings(user_id)
    vq = VIDEO_QUALITY_OPTIONS.get(settings["video_quality"], settings["video_quality"])
    aq = AUDIO_QUALITY_OPTIONS.get(settings["audio_quality"], settings["audio_quality"])

    msg = get_text("settings_title", lang, vq=vq, aq=aq)
    await safe_edit_message(
        query,
        msg,
        reply_markup=settings_keyboard(lang)
    )


async def btn_set_video_quality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض قائمة جودة الفيديو في الإعدادات"""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    await safe_edit_message(
        query,
        get_text("settings_video_title", lang),
        reply_markup=settings_video_quality_keyboard(lang)
    )


async def btn_set_audio_quality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض قائمة جودة الصوت في الإعدادات"""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    await safe_edit_message(
        query,
        get_text("settings_audio_title", lang),
        reply_markup=settings_audio_quality_keyboard(lang)
    )


async def btn_save_video_quality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """حفظ إعداد جودة الفيديو"""
    query = update.callback_query
    quality = query.data.split("|")[1]
    user_id = query.from_user.id
    lang = get_user_lang(user_id)

    settings = get_user_settings(user_id)
    settings["video_quality"] = quality
    quality_name = VIDEO_QUALITY_OPTIONS.get(quality, quality)

    await query.answer(get_text("settings_saved", lang, val=quality_name), show_alert=False)
    await btn_menu_settings(update, context)


async def btn_save_audio_quality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """حفظ إعداد جودة الصوت"""
    query = update.callback_query
    quality = query.data.split("|")[1]
    user_id = query.from_user.id
    lang = get_user_lang(user_id)

    settings = get_user_settings(user_id)
    settings["audio_quality"] = quality
    quality_name = AUDIO_QUALITY_OPTIONS.get(quality, quality)

    await query.answer(get_text("settings_saved", lang, val=quality_name), show_alert=False)
    await btn_menu_settings(update, context)


async def btn_set_bot_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض قائمة اختيار لغة البوت"""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    await safe_edit_message(
        query,
        get_text("settings_lang_title", lang),
        reply_markup=settings_lang_keyboard(lang)
    )


async def btn_save_bot_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """حفظ اختيار اللغة وإعادة عرض الإعدادات بالجديدة"""
    query = update.callback_query
    new_lang = query.data.split("|")[1]
    user_id = query.from_user.id

    set_user_lang(user_id, new_lang)
    lang = new_lang  # استخدام اللغة الجديدة فوراً

    await query.answer(get_text("settings_lang_saved", lang), show_alert=True)

    # إعادة عرض صفحة الإعدادات باللغة الجديدة
    settings = get_user_settings(user_id)
    vq = VIDEO_QUALITY_OPTIONS.get(settings["video_quality"], settings["video_quality"])
    aq = AUDIO_QUALITY_OPTIONS.get(settings["audio_quality"], settings["audio_quality"])
    await safe_edit_message(
        query,
        get_text("settings_title", lang, vq=vq, aq=aq),
        reply_markup=settings_keyboard(lang)
    )
