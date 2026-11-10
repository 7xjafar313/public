"""
downloader.py — منطق التحميل باستخدام yt-dlp
"""
import os
import asyncio
import logging
import shutil
from pathlib import Path
from typing import Optional, Callable
from concurrent.futures import ThreadPoolExecutor

import yt_dlp

from config import DOWNLOAD_DIR, MAX_FILE_SIZE_BYTES
from utils.helpers import ensure_dir, sanitize_filename

logger = logging.getLogger(__name__)

# Thread pool للتحميل غير المتزامن
_executor = ThreadPoolExecutor(max_workers=4)


def get_ffmpeg_location() -> Optional[str]:
    """تحديد مجلد FFMPEG ديناميكياً للويندوز ولينكس (Render)"""
    if os.name == "nt":
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(os.path.join(current_dir, "ffmpeg.exe")):
            return current_dir
    # على لينكس (Render)
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        return os.path.dirname(ffmpeg_bin)
    # خيار احتياطي افتراضي للينكس
    if os.path.exists("/usr/bin/ffmpeg"):
        return "/usr/bin"
    return None


def get_cookie_file() -> Optional[str]:
    """العثور على ملف الكوكيز أو استخراجه من متغيرات البيئة"""
    # 1. إذا تم توفير محتوى الكوكيز عبر متغير بيئة COOKIES_CONTENT في Render
    env_cookies = os.getenv("COOKIES_CONTENT", "").strip()
    if env_cookies:
        cookie_path = os.path.join(DOWNLOAD_DIR, "env_cookies.txt")
        try:
            with open(cookie_path, "w", encoding="utf-8") as f:
                f.write(env_cookies)
            return cookie_path
        except Exception:
            pass

    # 2. فحص وجود cookies.txt في مجلد المشروع
    root_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(root_dir, "cookies.txt"),
        "cookies.txt",
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.getsize(c) > 10:
            return c
    return None


def clean_url(url: str) -> str:
    """تنظيف الرابط من معاملات التتبع مثل ?igsh= أو ?mdxt= التي تسبب مشاكل مع بعض المنصات"""
    if "instagram.com" in url or "tiktok.com" in url:
        return url.split("?")[0]
    return url


def get_ydl_opts(extra_opts: Optional[dict] = None) -> dict:
    """تجهيز إعدادات yt-dlp الأساسية مع دعم الكوكيز والهيدرز المحدثة"""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "ffmpeg_location": get_ffmpeg_location(),
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        },
    }

    # إضافة ملف الكوكيز إن وُجد (مهم جداً لإنستغرام ويوتيوب)
    cookie_file = get_cookie_file()
    if cookie_file:
        opts["cookiefile"] = cookie_file

    if extra_opts:
        opts.update(extra_opts)
    return opts


# ==================== جلب معلومات الميديا ====================
def _extract_info(url: str, download: bool = False) -> dict:
    """استخراج معلومات الميديا (متزامن - يُستدعى في thread)"""
    target_url = clean_url(url)
    ydl_opts = get_ydl_opts({
        "extract_flat": "in_playlist" if not download else False,
    })
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(target_url, download=download)


async def get_media_info(url: str) -> Optional[dict]:
    """جلب معلومات الميديا بشكل غير متزامن"""
    loop = asyncio.get_event_loop()
    try:
        info = await loop.run_in_executor(_executor, _extract_info, url)
        return info
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting info: {e}")
        return None


# ==================== تحميل الفيديو ====================
def _download_video(url: str, quality: str, output_dir: str,
                    progress_hook: Optional[Callable] = None) -> Optional[str]:
    """تحميل فيديو (متزامن)"""
    ensure_dir(output_dir)

    # صيغة مرنة تعمل مع يوتيوب وإنستغرام وتيك توك وجميع المواقع
    if quality == "best":
        fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best"
    else:
        fmt = (
            f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo[height<={quality}]+bestaudio/"
            f"best[height<={quality}][ext=mp4]/"
            f"best[height<={quality}]/best"
        )

    ydl_opts = get_ydl_opts({
        "format": fmt,
        "outtmpl": os.path.join(output_dir, "%(title).80s.%(ext)s"),
        "merge_output_format": "mp4",
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",
        }],
    })

    if progress_hook:
        ydl_opts["progress_hooks"] = [progress_hook]

    target_url = clean_url(url)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=True)
            filename = ydl.prepare_filename(info)
            # تأكد من الامتداد الصحيح بعد الدمج
            if not os.path.exists(filename):
                base = os.path.splitext(filename)[0]
                for ext in ["mp4", "mkv", "webm", "avi"]:
                    candidate = f"{base}.{ext}"
                    if os.path.exists(candidate):
                        return candidate
            return filename
    except Exception as e:
        logger.error(f"Video download error: {e}")
        raise


async def download_video(url: str, quality: str = "best",
                         output_dir: str = DOWNLOAD_DIR,
                         progress_hook: Optional[Callable] = None) -> Optional[str]:
    """تحميل فيديو بشكل غير متزامن"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        _download_video,
        url, quality, output_dir, progress_hook
    )


# ==================== تحميل الصوت ====================
def _download_audio(url: str, quality: str, output_dir: str,
                    progress_hook: Optional[Callable] = None) -> Optional[str]:
    """تحميل صوت بصيغة MP3 (متزامن)"""
    ensure_dir(output_dir)

    ydl_opts = get_ydl_opts({
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title).80s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": quality,
        }],
    })

    if progress_hook:
        ydl_opts["progress_hooks"] = [progress_hook]

    target_url = clean_url(url)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=True)
            filename = ydl.prepare_filename(info)
            base = os.path.splitext(filename)[0]
            mp3_path = f"{base}.mp3"
            if os.path.exists(mp3_path):
                return mp3_path
            return filename
    except Exception as e:
        logger.error(f"Audio download error: {e}")
        raise


async def download_audio(url: str, quality: str = "192",
                         output_dir: str = DOWNLOAD_DIR,
                         progress_hook: Optional[Callable] = None) -> Optional[str]:
    """تحميل صوت بشكل غير متزامن"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        _download_audio,
        url, quality, output_dir, progress_hook
    )


# ==================== تحميل الصور ====================
def _download_images(url: str, output_dir: str) -> list[str]:
    """تحميل الصور (متزامن)"""
    ensure_dir(output_dir)

    ydl_opts = get_ydl_opts({
        "format": "best",
        "outtmpl": os.path.join(output_dir, "%(title).80s_%(autonumber)s.%(ext)s"),
        "writethumbnail": True,
        "skip_download": True,
    })

    downloaded = []
    target_url = clean_url(url)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=True)
            # ابحث عن الصور المحملة
            for file in Path(output_dir).glob("*"):
                if file.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
                    downloaded.append(str(file))
    except Exception as e:
        logger.error(f"Image download error: {e}")
        raise

    return downloaded


async def download_images(url: str, output_dir: str = DOWNLOAD_DIR) -> list[str]:
    """تحميل الصور بشكل غير متزامن"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _download_images, url, output_dir)


# ==================== تحميل قائمة تشغيل ====================
def _download_playlist(url: str, as_audio: bool, output_dir: str,
                        progress_hook: Optional[Callable] = None) -> list[str]:
    """تحميل قائمة تشغيل كاملة (متزامن)"""
    ensure_dir(output_dir)

    if as_audio:
        ydl_opts = get_ydl_opts({
            "format": "bestaudio/best",
            "outtmpl": os.path.join(output_dir, "%(playlist_index)s - %(title).60s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        ydl_opts = get_ydl_opts({
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": os.path.join(output_dir, "%(playlist_index)s - %(title).60s.%(ext)s"),
            "merge_output_format": "mp4",
        })

    if progress_hook:
        ydl_opts["progress_hooks"] = [progress_hook]

    downloaded_files = []
    target_url = clean_url(url)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=True)
            entries = info.get("entries", [])
            for entry in entries:
                if entry:
                    fp = ydl.prepare_filename(entry)
                    if os.path.exists(fp):
                        downloaded_files.append(fp)
    except Exception as e:
        logger.error(f"Playlist download error: {e}")
        raise

    return downloaded_files


async def download_playlist(url: str, as_audio: bool = False,
                             output_dir: str = DOWNLOAD_DIR,
                             progress_hook: Optional[Callable] = None) -> list[str]:
    """تحميل قائمة تشغيل بشكل غير متزامن"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        _download_playlist,
        url, as_audio, output_dir, progress_hook
    )


# ==================== دوال مساعدة ====================
def check_file_size(filepath: str) -> tuple[bool, int]:
    """التحقق من حجم الملف"""
    size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
    return size <= MAX_FILE_SIZE_BYTES, size


def delete_file(filepath: str) -> None:
    """حذف ملف بعد الإرسال"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Deleted: {filepath}")
    except Exception as e:
        logger.warning(f"Could not delete {filepath}: {e}")
