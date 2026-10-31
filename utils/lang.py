"""
utils/lang.py — ملف الترجمة لجميع نصوص وقوائم البوت (العربية والإنجليزية)
"""
from config import BOT_USERNAME, BOT_OWNER, BOT_PROGRAMMER, BOT_VERSION, MAX_FILE_SIZE_MB

# قاموس النصوص المترجمة
TRANSLATIONS = {
    "ar": {
        # القائمة الترحيبية
        "welcome": """
🤖 <b>مرحباً بك في بوت التحميل الشامل!</b>

أنا بوت قوي يستخدم <b>yt-dlp</b> لتحميل المحتوى من أكثر من <b>1000 موقع</b> 🌐

<b>المواقع المدعومة تشمل:</b>
▪️ YouTube & YouTube Music
▪️ Instagram (فيديو، صور، ريلز)
▪️ Twitter / X
▪️ TikTok
▪️ Facebook
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
""".format(bot=BOT_USERNAME, owner=BOT_OWNER, programmer=BOT_PROGRAMMER),

        # المساعدة
        "help": """
📖 <b>دليل الاستخدام</b>

<b>الطريقة الأساسية:</b>
أرسل الرابط مباشرةً في المحادثة وسأعرض لك خيارات التحميل.

<b>الأوامر المتاحة:</b>
/start — الشاشة الرئيسية
/help — هذه الرسالة
/settings — إعدادات التحميل واللغة
/status — حالة البوت
/about — معلومات البوت

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
""".format(max_size=MAX_FILE_SIZE_MB, bot=BOT_USERNAME, owner=BOT_OWNER, programmer=BOT_PROGRAMMER),

        # حول البوت
        "about": """
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
""".format(bot=BOT_USERNAME, owner=BOT_OWNER, programmer=BOT_PROGRAMMER, version=BOT_VERSION),

        # الأزرار والترجمات العامة
        "btn_video": "🎥 فيديو",
        "btn_audio": "🎵 صوت MP3",
        "btn_image": "📷 صور فقط",
        "btn_info": "ℹ️ معلومات",
        "btn_playlist": "📋 قائمة تشغيل",
        "btn_cancel": "❌ إلغاء",
        "btn_back": "🔙 رجوع",
        "btn_home": "🏠 الرئيسية",
        "btn_settings_video": "🎥 جودة الفيديو الافتراضية",
        "btn_settings_audio": "🎵 جودة الصوت الافتراضية",
        "btn_settings_lang": "🌐 لغة البوت / Language",
        "btn_back_settings": "🔙 رجوع للإعدادات",
        
        # نصوص التحميل
        "fetching_info": "🔍 جاري جلب معلومات الميديا من <b>{domain}</b>...",
        "invalid_url": "⚠️ يبدو أن هذا ليس رابطاً صحيحاً!\n\nأرسل لي رابطاً مثل:\n• https://youtube.com/watch?v=...\n• https://instagram.com/p/...\n• https://tiktok.com/@user/video/...",
        "fetch_error": "❌ لم أستطع جلب معلومات هذا الرابط.\n\nتأكد من:\n• أن الرابط صحيح\n• أن المحتوى عام (غير خاص)\n• أن الموقع مدعوم من yt-dlp",
        "fetch_exception": "❌ حدث خطأ أثناء جلب معلومات الميديا.\n<code>{err}</code>",
        "downloading": "⏳ <b>جاري التحميل...</b>\nيرجى الانتظار",
        "downloading_progress": "⬇️ <b>جاري التحميل...</b>\n\n{bar}\n📦 {downloaded} / {total}\n🚀 السرعة: {speed}\n⏱️ المتبقي: {eta}",
        "uploading": "📤 <b>جاري الرفع على تيليجرام...</b>\n📦 الحجم: {size}",
        "sent_success": "✅ تم التحميل بنجاح! 🎉\n🌐 {domain}",
        "sent_success_compress": "✅ تم التحميل بنجاح! 🎉\n🔧 تم ضغطه من {old_size} إلى {new_size}\n🌐 {domain}",
        "send_done": "✅ <b>تم الإرسال بنجاح!</b>",
        "cancelled": "❌ تم إلغاء التحميل.",
        "download_failed": "❌ <b>فشل التحميل!</b>\n\n<code>{err}</code>\n\nجرب رابطاً آخر أو جودة مختلفة.",
        "active_download_exists": "⚠️ لديك تحميل جارٍ بالفعل!",
        "file_too_large": "⚠️ <b>الملف كبير جداً!</b>\n\nحجم الملف: {size}\nالحد الأقصى: {max_size}MB\n\nجرب اختيار جودة أقل.",
        "file_too_large_compress_failed": "⚠️ <b>الملف كبير جداً ولا يمكن ضغطه كافياً!</b>\n\nالحجم الأصلي: {size}\nالحد الأقصى: {max_size}MB\n\nجرب تحميله كصوت أو باختيار جودة أقل:",
        "compressing": "📦 <b>الملف كبير جداً ({size})...</b>\n\n🔧 <b>جاري الضغط الذكي تلقائياً...</b>\nقد يستغرق هذا بضع ثوانٍ.",
        "uploading_compressed": "📤 <b>جاري رفع الفيديو المضغوط...</b>\n📦 الحجم بعد الضغط: {size}",
        
        # القوائم والتشغيل
        "playlist_title": "📋 <b>قائمة تشغيل</b>\n\n📝 <b>الاسم:</b> {title}\n🎬 <b>عدد الفيديوهات:</b> {count}\n👤 <b>القناة:</b> {uploader}\n\n<i>اختر طريقة التحميل:</i>",
        "btn_playlist_all": "📥 تحميل الكل ({count} فيديو)",
        "btn_playlist_audio": "🎵 الكل كصوت MP3",
        "playlist_finished": "✅ <b>تم الانتهاء!</b>\nتم إرسال {sent} من {total} ملف.",
        "playlist_failed": "❌ فشل تحميل القائمة!\n<code>{err}</code>",
        "playlist_size_warning": "⚠️ تجاوز الحجم: {name} ({size})",
        
        # الصور
        "images_loading": "📷 <b>جاري تحميل الصور...</b>",
        "images_not_found": "❌ لم يتم العثور على صور.\nجرب تحميله كفيديو بدلاً من ذلك.",
        "images_uploading": "📤 جاري رفع {count} صورة...",
        "images_caption": "📷 صورة {index}/{total}",
        "images_finished": "✅ <b>تم إرسال {count} صورة!</b>",
        "images_failed": "❌ فشل تحميل الصور!\n<code>{err}</code>",
        
        # معلومات الميديا التفصيلية
        "info_title": "ℹ️ <b>معلومات الميديا</b>\n\n📝 <b>العنوان:</b>\n{title}\n\n⏱️ <b>المدة:</b> {duration}\n👤 <b>الرافع:</b> {uploader}\n👁️ <b>المشاهدات:</b> {views}\n❤️ <b>الإعجابات:</b> {likes}\n🎬 <b>الجودات المتاحة:</b> {qualities}",
        "info_loading": "🔍 جاري جلب المعلومات...",
        "info_fetching_details": "🔍 <b>جاري جلب المعلومات التفصيلية...</b>",
        
        # الإعدادات
        "settings_title": "⚙️ <b>الإعدادات</b>\n\n🎥 <b>جودة الفيديو الافتراضية:</b>\n└ {vq}\n\n🎵 <b>جودة الصوت الافتراضية:</b>\n└ {aq}\n\nاختر ما تريد تغييره:",
        "settings_video_title": "🎥 <b>اختر جودة الفيديو الافتراضية:</b>",
        "settings_audio_title": "🎵 <b>اختر جودة الصوت الافتراضية:</b>",
        "settings_lang_title": "🌐 <b>اختر لغة البوت / Select Language:</b>",
        "settings_saved": "✅ تم الحفظ: {val}",
        "settings_lang_saved": "✅ تم تغيير اللغة إلى العربية!",
        
        # أخرى
        "blocked_alert": "🚫 عذراً، تم حظر حسابك من استخدام هذا البوت!",
        "spam_alert": "⚠️ **الرجاء عدم إرسال الرسائل بسرعة كبيرة!**\nانتظر قليلاً ثم حاول مجدداً.",
        "url_expired": "⚠️ عذراً، انتهت صلاحية هذا الرابط. يرجى إرسال الرابط مجدداً.",
        "select_vq": "🎥 <b>اختر جودة الفيديو:</b>",
        "select_aq": "🎵 <b>اختر جودة الصوت (MP3):</b>",
        "btn_menu_video_msg": "🎥 <b>تحميل فيديو</b>\n\nأرسل رابط الفيديو الذي تريد تحميله:",
        "btn_menu_audio_msg": "🎵 <b>تحميل صوت MP3</b>\n\nأرسل رابط الفيديو أو الأغنية:",
        "btn_menu_image_msg": "📷 <b>تحميل صور</b>\n\nأرسل رابط الصفحة (Instagram, Twitter, Pinterest...):",
        "btn_menu_playlist_msg": "📋 <b>تحميل قائمة تشغيل</b>\n\nأرسل رابط قائمة تشغيل YouTube:",
        "btn_cancel_action": "تم الإلغاء",
        "btn_cancel_done": "❌ <b>تم الإلغاء.</b>",
    },
    "en": {
        # Welcome Screen
        "welcome": """
🤖 <b>Welcome to the Ultimate Downloader Bot!</b>

I am a powerful bot powered by <b>yt-dlp</b> to download media from over <b>1000 websites</b> 🌐

<b>Supported platforms include:</b>
▪️ YouTube & YouTube Music
▪️ Instagram (Video, Photos, Reels)
▪️ Twitter / X
▪️ TikTok
▪️ Facebook
▪️ SoundCloud (Music)
▪️ Reddit, Pinterest
▪️ Twitch (Clips)
▪️ And over 1000 more websites!

<b>How to use me?</b>
Just send me <b>any video or photo link</b> directly, and I'll do the rest! 🚀

Press /help for guide or use the buttons below 👇

━━━━━━━━━━━━━━━━━━
🤖 Bot: {bot}
👑 Owner: {owner}
👨‍💻 Programmer: {programmer}
━━━━━━━━━━━━━━━━━━
""".format(bot=BOT_USERNAME, owner=BOT_OWNER, programmer=BOT_PROGRAMMER),

        # Help Screen
        "help": """
📖 <b>User Guide</b>

<b>Basic Usage:</b>
Send the link directly in the chat, and I will show you the download options.

<b>Available Commands:</b>
/start — Main Menu
/help — This message
/settings — Download & Language Settings
/status — Bot Status
/about — Bot Information

<b>Download Options:</b>
🎥 <b>Video</b> — Choose quality from 144p up to 4K
🎵 <b>Audio Only</b> — MP3 quality up to 320kbps
📷 <b>Photos</b> — For Instagram and other platforms
📋 <b>Playlist</b> — All videos of a YouTube playlist
ℹ️ <b>Information</b> — Show media details

<b>Notes:</b>
⚠️ Max File Size: {max_size}MB
⚠️ Some platforms may require logging in

━━━━━━━━━━━━━━━━━━
🤖 Bot: {bot}
👑 Owner: {owner}
👨‍💻 Programmer: {programmer}
<i>All rights reserved © 2025</i>
━━━━━━━━━━━━━━━━━━
""".format(max_size=MAX_FILE_SIZE_MB, bot=BOT_USERNAME, owner=BOT_OWNER, programmer=BOT_PROGRAMMER),

        # About Screen
        "about": """
ℹ️ <b>About the Bot</b>

🤖 <b>Name:</b> Ultimate Downloader Bot
🔗 <b>Username:</b> {bot}
🌐 <b>Version:</b> v{version}

<b>Features:</b>
✅ Download from 1000+ sites
✅ Support multiple qualities up to 4K
✅ Extract audio in MP3 format
✅ Download images and Reels
✅ Download full playlists
✅ Live progress bar

━━━━━━━━━━━━━━━━━━
👑 <b>Owner:</b> {owner}
👨‍💻 <b>Programmer:</b> {programmer}
<i>All rights reserved © 2025</i>
━━━━━━━━━━━━━━━━━━
""".format(bot=BOT_USERNAME, owner=BOT_OWNER, programmer=BOT_PROGRAMMER, version=BOT_VERSION),

        # Buttons and General Translations
        "btn_video": "🎥 Video",
        "btn_audio": "🎵 Audio MP3",
        "btn_image": "📷 Images Only",
        "btn_info": "ℹ️ Info",
        "btn_playlist": "📋 Playlist",
        "btn_cancel": "❌ Cancel",
        "btn_back": "🔙 Back",
        "btn_home": "🏠 Home",
        "btn_settings_video": "🎥 Default Video Quality",
        "btn_settings_audio": "🎵 Default Audio Quality",
        "btn_settings_lang": "🌐 Language / لغة البوت",
        "btn_back_settings": "🔙 Back to Settings",
        
        # Download Texts
        "fetching_info": "🔍 Fetching media info from <b>{domain}</b>...",
        "invalid_url": "⚠️ That doesn't seem to be a valid link!\n\nSend me a link like:\n• https://youtube.com/watch?v=...\n• https://instagram.com/p/...\n• https://tiktok.com/@user/video/...",
        "fetch_error": "❌ Could not fetch media info for this link.\n\nMake sure:\n• The link is correct\n• The content is public (not private)\n• The website is supported by yt-dlp",
        "fetch_exception": "❌ An error occurred while fetching media info.\n<code>{err}</code>",
        "downloading": "⏳ <b>Downloading...</b>\nPlease wait",
        "downloading_progress": "⬇️ <b>Downloading...</b>\n\n{bar}\n📦 {downloaded} / {total}\n🚀 Speed: {speed}\n⏱️ ETA: {eta}",
        "uploading": "📤 <b>Uploading to Telegram...</b>\n📦 Size: {size}",
        "sent_success": "✅ Downloaded successfully! 🎉\n🌐 {domain}",
        "sent_success_compress": "✅ Downloaded successfully! 🎉\n🔧 Compressed from {old_size} to {new_size}\n🌐 {domain}",
        "send_done": "✅ <b>Sent successfully!</b>",
        "cancelled": "❌ Download cancelled.",
        "download_failed": "❌ <b>Download failed!</b>\n\n<code>{err}</code>\n\nTry another link or a different quality.",
        "active_download_exists": "⚠️ You already have an active download running!",
        "file_too_large": "⚠️ <b>File is too large!</b>\n\nFile size: {size}\nLimit: {max_size}MB\n\nTry selecting a lower quality.",
        "file_too_large_compress_failed": "⚠️ <b>File is too large and cannot be compressed enough!</b>\n\nOriginal size: {size}\nLimit: {max_size}MB\n\nTry downloading as audio or selecting a lower quality:",
        "compressing": "📦 <b>File is too large ({size})...</b>\n\n🔧 <b>Compressing automatically...</b>\nPlease wait.",
        "uploading_compressed": "📤 <b>Uploading compressed video...</b>\n📦 Compressed size: {size}",
        
        # Playlists
        "playlist_title": "📋 <b>Playlist</b>\n\n📝 <b>Name:</b> {title}\n🎬 <b>Videos Count:</b> {count}\n👤 <b>Channel:</b> {uploader}\n\n<i>Choose download method:</i>",
        "btn_playlist_all": "📥 Download All ({count} videos)",
        "btn_playlist_audio": "🎵 All as MP3",
        "playlist_finished": "✅ <b>Done!</b>\nSent {sent} of {total} files.",
        "playlist_failed": "❌ Playlist download failed!\n<code>{err}</code>",
        "playlist_size_warning": "⚠️ Exceeded size: {name} ({size})",
        
        # Images
        "images_loading": "📷 <b>Downloading images...</b>",
        "images_not_found": "❌ No images found.\nTry downloading as a video instead.",
        "images_uploading": "📤 Uploading {count} images...",
        "images_caption": "📷 Image {index}/{total}",
        "images_finished": "✅ <b>Sent {count} images!</b>",
        "images_failed": "❌ Failed to download images!\n<code>{err}</code>",
        
        # Detailed Media Info
        "info_title": "ℹ️ <b>Media Info</b>\n\n📝 <b>Title:</b>\n{title}\n\n⏱️ <b>Duration:</b> {duration}\n👤 <b>Uploader:</b> {uploader}\n👁️ <b>Views:</b> {views}\n❤️ <b>Likes:</b> {likes}\n🎬 <b>Available Qualities:</b> {qualities}",
        "info_loading": "🔍 Fetching info...",
        "info_fetching_details": "🔍 <b>Fetching detailed info...</b>",
        
        # Settings
        "settings_title": "⚙️ <b>Settings</b>\n\n🎥 <b>Default Video Quality:</b>\n└ {vq}\n\n🎵 <b>Default Audio Quality:</b>\n└ {aq}\n\nSelect what you want to change:",
        "settings_video_title": "🎥 <b>Select default video quality:</b>",
        "settings_audio_title": "🎵 <b>Select default audio quality:</b>",
        "settings_lang_title": "🌐 <b>Select Language / اختر لغة البوت:</b>",
        "settings_saved": "✅ Saved: {val}",
        "settings_lang_saved": "✅ Language changed to English!",
        
        # Other
        "blocked_alert": "🚫 Sorry, your account has been blocked from using this bot!",
        "spam_alert": "⚠️ **Please do not spam!**\nWait a moment and try again.",
        "url_expired": "⚠️ Sorry, this link has expired. Please send it again.",
        "select_vq": "🎥 <b>Select Video Quality:</b>",
        "select_aq": "🎵 <b>Select Audio Quality (MP3):</b>",
        "btn_menu_video_msg": "🎥 <b>Download Video</b>\n\nSend the link of the video you want to download:",
        "btn_menu_audio_msg": "🎵 <b>Download Audio MP3</b>\n\nSend the link of the video or song:",
        "btn_menu_image_msg": "📷 <b>Download Images</b>\n\nSend the link of the page (Instagram, Twitter, Pinterest...):",
        "btn_menu_playlist_msg": "📋 <b>Download Playlist</b>\n\nSend the link of the YouTube playlist:",
        "btn_cancel_action": "Cancelled",
        "btn_cancel_done": "❌ <b>Cancelled.</b>",
    }
}

def get_text(key: str, lang: str = "ar", **kwargs) -> str:
    """الحصول على النص المناسب للغة مع تعبئة المتغيرات إن وجدت"""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["ar"])
    text_template = lang_dict.get(key, TRANSLATIONS["ar"].get(key, ""))
    
    if text_template and kwargs:
        try:
            return text_template.format(**kwargs)
        except Exception:
            return text_template
    return text_template
