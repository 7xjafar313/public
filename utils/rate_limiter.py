"""
utils/rate_limiter.py — منع السبام والرسائل المتكررة من المستخدمين
"""
import time

# قاموس لتسجيل أوقات إرسال الرسائل لكل مستخدم في الذاكرة
user_messages: dict[int, list[float]] = {}

def check_rate_limit(user_id: int, limit: int = 3, window: int = 5) -> bool:
    """
    التحقق مما إذا كان المستخدم قد تجاوز الحد المسموح به من الرسائل.
    
    :param user_id: معرّف المستخدم
    :param limit: عدد الرسائل الأقصى المسموح به
    :param window: الفترة الزمنية بالثواني
    :return: True إذا تجاوز الحد (سبام)، False إذا كانت طبيعية
    """
    now = time.time()
    
    if user_id not in user_messages:
        user_messages[user_id] = [now]
        return False
        
    # جلب التوقيتات وتصفية القديمة التي تقع خارج النافذة الزمنية
    timestamps = [t for t in user_messages[user_id] if now - t < window]
    
    if len(timestamps) >= limit:
        # المستخدم تجاوز الحد
        return True
        
    # إضافة التوقيت الحالي وتحديث الذاكرة
    timestamps.append(now)
    user_messages[user_id] = timestamps
    return False
