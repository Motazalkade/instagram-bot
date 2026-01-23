"""
نظام التحقق من توفر اليوزرات على إنستجرام - النسخة 3
يستخدم طرق متعددة للتحقق الدقيق
"""

import asyncio
from typing import Dict, List
import logging
import os
import requests
from instagrapi import Client
from instagrapi.exceptions import UserNotFound, ClientError, LoginRequired

logger = logging.getLogger(__name__)


class InstagramCheckerV3:
    """فئة متقدمة للتحقق من توفر اليوزرات على إنستجرام"""
    
    def __init__(self, username: str = None, password: str = None):
        """
        تهيئة المدقق مع المصادقة الاختيارية
        
        Args:
            username (str): اسم المستخدم (أو من متغيرات البيئة)
            password (str): كلمة المرور (أو من متغيرات البيئة)
        """
        self.client = Client()
        self.delay = 1.5  # تأخير بين الطلبات
        self.is_authenticated = False
        
        # محاولة الحصول على بيانات المصادقة
        self.ig_username = username or os.getenv('INSTAGRAM_USERNAME')
        self.ig_password = password or os.getenv('INSTAGRAM_PASSWORD')
        
        # محاولة تسجيل الدخول إذا كانت البيانات متوفرة
        if self.ig_username and self.ig_password:
            self._login()
    
    def _login(self):
        """تسجيل الدخول إلى إنستجرام"""
        try:
            logger.info("جاري تسجيل الدخول إلى إنستجرام...")
            self.client.login(self.ig_username, self.ig_password)
            self.is_authenticated = True
            logger.info("✅ تم تسجيل الدخول بنجاح")
        except Exception as e:
            logger.warning(f"⚠️ فشل تسجيل الدخول: {str(e)[:50]}")
            self.is_authenticated = False
    
    def _check_via_http(self, username: str) -> Dict[str, any]:
        """
        التحقق عن طريق HTTP مباشر
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            url = f"https://www.instagram.com/{username}/"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 404:
                return {'method': 'http', 'available': True}
            elif response.status_code == 200:
                # تحقق من محتوى الصفحة
                if "User Not Found" in response.text or "not found" in response.text.lower():
                    return {'method': 'http', 'available': True}
                return {'method': 'http', 'available': False}
            else:
                return {'method': 'http', 'available': None}
        
        except Exception as e:
            logger.warning(f"HTTP check failed: {e}")
            return {'method': 'http', 'available': None}
    
    async def check_username_availability(self, username: str) -> Dict[str, any]:
        """
        التحقق من توفر يوزر واحد بشكل حقيقي
        استخدام طرق متعددة للتحقق
        
        Args:
            username (str): اليوزر المراد التحقق منه
        
        Returns:
            Dict: قاموس يحتوي على:
                - 'username': اليوزر
                - 'available': هل اليوزر متاح (True/False)
                - 'status': حالة اليوزر
                - 'error': رسالة الخطأ إن وجدت
        """
        try:
            # الطريقة 1: استخدام Instagrapi
            try:
                user_info = self.client.user_info_by_username(username)
                # إذا وجدنا المستخدم، فهو غير متاح
                return {
                    'username': username,
                    'available': False,
                    'status': f'مستخدم بالفعل',
                    'error': None,
                    'user_id': user_info.pk,
                    'method': 'instagrapi'
                }
            
            except UserNotFound:
                # إذا لم نجد المستخدم، فهو متاح
                return {
                    'username': username,
                    'available': True,
                    'status': 'متاح للاستخدام ✅',
                    'error': None,
                    'user_id': None,
                    'method': 'instagrapi'
                }
            
            except (LoginRequired, ClientError) as e:
                # إذا فشل Instagrapi، جرب HTTP
                logger.info(f"Instagrapi failed for {username}, trying HTTP method...")
                http_result = self._check_via_http(username)
                
                if http_result['available'] is not None:
                    return {
                        'username': username,
                        'available': http_result['available'],
                        'status': 'متاح للاستخدام ✅' if http_result['available'] else 'مستخدم بالفعل',
                        'error': None,
                        'user_id': None,
                        'method': 'http'
                    }
                
                # إذا فشلت كلا الطريقتين
                return {
                    'username': username,
                    'available': None,
                    'status': 'خطأ في التحقق',
                    'error': str(e)[:30],
                    'user_id': None,
                    'method': 'failed'
                }
        
        except Exception as e:
            logger.error(f"خطأ في فحص {username}: {e}")
            return {
                'username': username,
                'available': None,
                'status': 'خطأ غير متوقع',
                'error': str(e)[:30],
                'user_id': None,
                'method': 'error'
            }
    
    async def check_multiple_usernames(self, usernames: List[str]) -> List[Dict]:
        """
        التحقق من عدة يوزرات بشكل متسلسل
        
        Args:
            usernames (List[str]): قائمة اليوزرات المراد التحقق منها
        
        Returns:
            List[Dict]: قائمة بنتائج التحقق
        """
        results = []
        
        for i, username in enumerate(usernames):
            try:
                result = await self.check_username_availability(username)
                results.append(result)
                
                # تأخير بين الطلبات
                if i < len(usernames) - 1:
                    await asyncio.sleep(self.delay)
            
            except Exception as e:
                logger.error(f"خطأ في فحص {username}: {e}")
                results.append({
                    'username': username,
                    'available': None,
                    'status': 'خطأ في المعالجة',
                    'error': str(e)[:30],
                    'user_id': None,
                    'method': 'error'
                })
        
        return results
    
    async def check_batch_usernames(self, usernames: List[str], batch_size: int = 2) -> List[Dict]:
        """
        التحقق من دفعة من اليوزرات
        
        Args:
            usernames (List[str]): قائمة اليوزرات
            batch_size (int): عدد الطلبات المتزامنة (افتراضي: 2)
        
        Returns:
            List[Dict]: قائمة بنتائج التحقق
        """
        results = []
        
        for i in range(0, len(usernames), batch_size):
            batch = usernames[i:i + batch_size]
            
            try:
                batch_results = await asyncio.gather(
                    *[self.check_username_availability(username) for username in batch],
                    return_exceptions=True
                )
                
                # معالجة النتائج
                for result in batch_results:
                    if isinstance(result, dict):
                        results.append(result)
                    else:
                        results.append({
                            'username': 'unknown',
                            'available': None,
                            'status': 'خطأ',
                            'error': 'خطأ في المعالجة',
                            'user_id': None,
                            'method': 'error'
                        })
                
                # تأخير أطول بين الدفعات
                if i + batch_size < len(usernames):
                    await asyncio.sleep(3)
            
            except Exception as e:
                logger.error(f"خطأ في معالجة الدفعة: {e}")
        
        return results
    
    def get_available_usernames(self, results: List[Dict]) -> List[str]:
        """استخراج اليوزرات المتاحة"""
        return [r['username'] for r in results if r.get('available') is True]
    
    def get_unavailable_usernames(self, results: List[Dict]) -> List[str]:
        """استخراج اليوزرات غير المتاحة"""
        return [r['username'] for r in results if r.get('available') is False]
    
    def get_error_usernames(self, results: List[Dict]) -> List[str]:
        """استخراج اليوزرات التي حدثت فيها أخطاء"""
        return [r['username'] for r in results if r.get('available') is None]


# مثال على الاستخدام
async def main():
    # استخدام مع المصادقة
    checker = InstagramCheckerV3(
        username='jbrn3870',
        password='zzxxcc123@#'
    )
    
    # قائمة اختبار
    test_usernames = ['instagram', 'test123456', 'xyz_random_user_123']
    
    print("جاري التحقق من اليوزرات...")
    results = await checker.check_batch_usernames(test_usernames)
    
    print("\nالنتائج:")
    for result in results:
        status = "متاح ✓" if result['available'] else "غير متاح ✗" if result['available'] is False else "خطأ ⚠"
        print(f"  {result['username']}: {status} - {result['status']} ({result['method']})")
    
    available = checker.get_available_usernames(results)
    print(f"\nاليوزرات المتاحة: {available}")


if __name__ == "__main__":
    asyncio.run(main())
