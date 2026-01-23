"""
نظام التحقق من توفر اليوزرات على إنستجرام باستخدام Instagrapi
يوفر نتائج حقيقية وموثوقة مع المصادقة
"""

import asyncio
from typing import Dict, List
import logging
import os
from instagrapi import Client
from instagrapi.exceptions import UserNotFound, ClientError, LoginRequired

logger = logging.getLogger(__name__)


class InstagramCheckerV2:
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
    
    async def check_username_availability(self, username: str) -> Dict[str, any]:
        """
        التحقق من توفر يوزر واحد بشكل حقيقي
        
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
            # محاولة الحصول على معلومات المستخدم
            user_info = self.client.user_info_by_username(username)
            
            # إذا وجدنا المستخدم، فهو غير متاح
            return {
                'username': username,
                'available': False,
                'status': f'مستخدم بالفعل - ID: {user_info.pk}',
                'error': None,
                'user_id': user_info.pk
            }
        
        except UserNotFound:
            # إذا لم نجد المستخدم، فهو متاح
            return {
                'username': username,
                'available': True,
                'status': 'متاح للاستخدام ✅',
                'error': None,
                'user_id': None
            }
        
        except LoginRequired:
            # يحتاج إلى تسجيل دخول
            return {
                'username': username,
                'available': None,
                'status': 'يحتاج إلى تسجيل دخول',
                'error': 'LoginRequired',
                'user_id': None
            }
        
        except ClientError as e:
            # خطأ من العميل (قد يكون حظر مؤقت)
            error_str = str(e).lower()
            if 'rate limit' in error_str or 'too many requests' in error_str:
                return {
                    'username': username,
                    'available': None,
                    'status': 'حظر مؤقت من إنستجرام',
                    'error': 'RateLimit',
                    'user_id': None
                }
            
            return {
                'username': username,
                'available': None,
                'status': 'خطأ في الاتصال',
                'error': f'ClientError: {str(e)[:30]}',
                'user_id': None
            }
        
        except Exception as e:
            # أي خطأ آخر
            error_str = str(e).lower()
            
            # محاولة تحديد نوع الخطأ
            if 'not found' in error_str or 'does not exist' in error_str:
                return {
                    'username': username,
                    'available': True,
                    'status': 'متاح للاستخدام ✅',
                    'error': None,
                    'user_id': None
                }
            
            return {
                'username': username,
                'available': None,
                'status': 'خطأ غير معروف',
                'error': f'Error: {str(e)[:30]}',
                'user_id': None
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
                    'user_id': None
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
                            'user_id': None
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
    checker = InstagramCheckerV2(
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
        print(f"  {result['username']}: {status} - {result['status']}")
    
    available = checker.get_available_usernames(results)
    print(f"\nاليوزرات المتاحة: {available}")


if __name__ == "__main__":
    asyncio.run(main())
