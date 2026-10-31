"""
utils/helpers.py — وظائف مساعدة للبوت
"""
import os
import re
import time
import shutil
from pathlib import Path
from typing import Optional


def is_valid_url(text: str) -> bool:
    """التحقق من أن النص رابط URL صحيح"""
    url_pattern = re.compile(
        r'https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE
    )
    return bool(url_pattern.match(text.strip()))


def format_size(size_bytes: int) -> str:
    """تحويل حجم الملف إلى صيغة مقروءة"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.2f} GB"


def format_duration(seconds: Optional[int]) -> str:
    """تحويل المدة بالثواني إلى صيغة مقروءة"""
    if not seconds:
        return "غير معروف"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def sanitize_filename(filename: str) -> str:
    """تنظيف اسم الملف من الأحرف غير المسموحة"""
    invalid_chars = r'<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:200]  # حد أقصى لطول الاسم


def ensure_dir(path: str) -> str:
    """إنشاء المجلد إذا لم يكن موجوداً"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(filepath: str) -> int:
    """الحصول على حجم الملف بالبايت"""
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0


def clean_downloads_dir(download_dir: str, max_age_hours: int = 24) -> None:
    """حذف الملفات القديمة من مجلد التحميل"""
    now = time.time()
    cutoff = now - (max_age_hours * 3600)
    
    try:
        for item in Path(download_dir).iterdir():
            if item.is_file() and item.stat().st_mtime < cutoff:
                item.unlink(missing_ok=True)
            elif item.is_dir() and item.stat().st_mtime < cutoff:
                shutil.rmtree(item, ignore_errors=True)
    except Exception:
        pass


def truncate_title(title: str, max_len: int = 50) -> str:
    """اختصار العنوان إذا كان طويلاً"""
    if len(title) <= max_len:
        return title
    return title[:max_len - 3] + "..."


def progress_bar(current: int, total: int, length: int = 10) -> str:
    """إنشاء شريط تقدم نصي"""
    if total == 0:
        return "░" * length
    filled = int(length * current / total)
    bar = "█" * filled + "░" * (length - filled)
    percent = (current / total) * 100
    return f"{bar} {percent:.1f}%"


def get_domain(url: str) -> str:
    """استخراج اسم الموقع من الرابط"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        return domain.split(".")[0].capitalize()
    except Exception:
        return "الموقع"
