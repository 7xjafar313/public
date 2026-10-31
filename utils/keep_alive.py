"""
utils/keep_alive.py — سيرفر ويب خفيف مع ميزة إرسال الطلبات الذاتية (Keep-Alive / Self-Ping)
مخصص لبيئة Render لمنع إيقاف الخدمة (Sleep Mode) والرد على فحص المنافذ (Health Check).
"""
import os
import json
import time
import threading
import logging
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

logger = logging.getLogger("keep_alive")

START_TIME = time.time()
ACTIVE_BOTS: list[str] = []


def register_bot(bot_name: str):
    """تسجيل اسم أو معرف البوت لإظهاره في صفحة الحالة"""
    if bot_name not in ACTIVE_BOTS:
        ACTIVE_BOTS.append(bot_name)


class KeepAliveHandler(BaseHTTPRequestHandler):
    """معالج طلبات الويب البسيط لإرجاع حالة البوتات لـ Render و UptimeRobot"""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

        uptime_sec = int(time.time() - START_TIME)
        hours, rem = divmod(uptime_sec, 3600)
        mins, secs = divmod(rem, 60)
        uptime_str = f"{hours}h {mins}m {secs}s"

        response_data = {
            "status": "online",
            "message": "All Telegram bots are running smoothly! 🚀",
            "uptime": uptime_str,
            "active_bots_count": len(ACTIVE_BOTS),
            "active_bots": ACTIVE_BOTS,
        }
        self.wfile.write(json.dumps(response_data, ensure_ascii=False, indent=2).encode("utf-8"))

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

    def log_message(self, format, *args):
        # كتم تسجيل الطلبات المتكررة لمنع امتلاء السجلات (logs)
        pass


def _self_ping_worker(target_url: str, interval_seconds: int = 480):
    """
    عامل في الخلفية يقوم بإرسال طلب HTTP إلى رابط Render كل 8 دقائق
    لمنع السيرفر من الدخول في وضع السكون (Sleep Mode)
    """
    logger.info(f"🔄 ميزة التنشيط الذاتي (Self-Ping) مفعّلة لرابط: {target_url} (كل {interval_seconds // 60} دقائق)")
    
    # انتظار أولي 45 ثانية قبل أول طلب لضمان جاهزية السيرفر بالكامل
    time.sleep(45)

    while True:
        try:
            req = urllib.request.Request(
                target_url,
                headers={"User-Agent": "Render-KeepAlive-Worker/1.0"}
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                logger.info(f"💓 [Self-Ping] تم إرسال طلب تنشيط للسيرفر بنجاح! كود الرد: {resp.status}")
        except Exception as e:
            logger.warning(f"⚠️ [Self-Ping] فشل إرسال طلب التنشيط: {e}")

        time.sleep(interval_seconds)


def start_keep_alive(port: int | None = None, ping_url: str | None = None):
    """
    بدء تشغيل سيرفر الويب وميزة التنشيط الذاتي في خيوط منفصلة (Threads)
    """
    # 1. تحديد المنفذ (Render يمرر متغير PORT تلقائياً)
    if port is None:
        port_env = os.getenv("PORT", "8000")
        try:
            port = int(port_env)
        except ValueError:
            port = 8000

    # 2. بدء سيرفر الويب
    try:
        server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        logger.info(f"🌐 خادم Keep-Alive يعمل الآن على المنفذ: {port} (متوافق مع Render Web Service)")
    except Exception as e:
        logger.error(f"❌ تعذر بدء خادم Keep-Alive على المنفذ {port}: {e}")
        return

    # 3. تفعيل التنشيط الذاتي إذا توفر الرابط
    # Render يضع تلقائياً متغير RENDER_EXTERNAL_URL
    target = ping_url or os.getenv("RENDER_EXTERNAL_URL") or os.getenv("KEEP_ALIVE_URL")
    if target:
        if not target.startswith("http://") and not target.startswith("https://"):
            target = "https://" + target
        ping_thread = threading.Thread(target=_self_ping_worker, args=(target,), daemon=True)
        ping_thread.start()
    else:
        logger.info("ℹ️ لم يتم العثور على رابط Render الخارجي بعد. بمجرد توفر RENDER_EXTERNAL_URL أو KEEP_ALIVE_URL سيعمل التنشيط الذاتي تلقائياً.")
