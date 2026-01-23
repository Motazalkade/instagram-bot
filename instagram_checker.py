"""
نظام التحقق من توفر اليوزرات على إنستجرام
يقوم بالتحقق من توفر اليوزرات عن طريق إرسال طلبات HTTP
"""

import aiohttp
import asyncio
from typing import Dict, List
import time


class InstagramChecker:
    """فئة للتحقق من توفر اليوزرات على إنستجرام"""
    
    def __init__(self):
        """تهيئة المدقق"""
        # رابط API إنستجرام للتحقق من توفر اليوزرات
        self.instagram_api_url = "https://www.instagram.com/api/v1/users/search/"
        
        # رؤوس الطلب
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # تأخير بين الطلبات (لتجنب الحظر)
        self.delay = 0.5
    
    async def check_username_availability(self, username: str) -> Dict[str, any]:
        """
        التحقق من توفر يوزر واحد
        
        Args:
            username (str): اليوزر المراد التحقق منه
        
        Returns:
            Dict: قاموس يحتوي على:
                - 'username': اليوزر
                - 'available': هل اليوزر متاح (True/False)
                - 'status_code': رمز الحالة HTTP
                - 'error': رسالة الخطأ إن وجدت
        """
        try:
            async with aiohttp.ClientSession() as session:
                # محاولة الوصول إلى صفحة المستخدم
                url = f"https://www.instagram.com/{username}/"
                
                async with session.get(url, headers=self.headers, timeout=10) as response:
                    # إذا كان الرد 404، فاليوزر متاح
                    if response.status == 404:
                        return {
                            'username': username,
                            'available': True,
                            'status_code': 404,
                            'error': None
                        }
                    # إذا كان الرد 200، فاليوزر مستخدم
                    elif response.status == 200:
                        return {
                            'username': username,
                            'available': False,
                            'status_code': 200,
                            'error': 'اليوزر مستخدم بالفعل'
                        }
                    else:
                        return {
                            'username': username,
                            'available': None,
                            'status_code': response.status,
                            'error': f'رد غير متوقع: {response.status}'
                        }
        
        except asyncio.TimeoutError:
            return {
                'username': username,
                'available': None,
                'status_code': None,
                'error': 'انتهت مهلة الانتظار'
            }
        except Exception as e:
            return {
                'username': username,
                'available': None,
                'status_code': None,
                'error': str(e)
            }
    
    async def check_multiple_usernames(self, usernames: List[str]) -> List[Dict]:
        """
        التحقق من عدة يوزرات
        
        Args:
            usernames (List[str]): قائمة اليوزرات المراد التحقق منها
        
        Returns:
            List[Dict]: قائمة بنتائج التحقق
        """
        results = []
        
        for username in usernames:
            result = await self.check_username_availability(username)
            results.append(result)
            
            # تأخير بين الطلبات
            await asyncio.sleep(self.delay)
        
        return results
    
    async def check_batch_usernames(self, usernames: List[str], batch_size: int = 5) -> List[Dict]:
        """
        التحقق من دفعة من اليوزرات بشكل متزامن
        
        Args:
            usernames (List[str]): قائمة اليوزرات
            batch_size (int): عدد الطلبات المتزامنة (افتراضي: 5)
        
        Returns:
            List[Dict]: قائمة بنتائج التحقق
        """
        results = []
        
        for i in range(0, len(usernames), batch_size):
            batch = usernames[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.check_username_availability(username) for username in batch]
            )
            results.extend(batch_results)
            
            # تأخير بين الدفعات
            if i + batch_size < len(usernames):
                await asyncio.sleep(1)
        
        return results
    
    def get_available_usernames(self, results: List[Dict]) -> List[str]:
        """
        استخراج اليوزرات المتاحة من النتائج
        
        Args:
            results (List[Dict]): نتائج التحقق
        
        Returns:
            List[str]: قائمة اليوزرات المتاحة
        """
        return [r['username'] for r in results if r['available'] is True]
    
    def get_unavailable_usernames(self, results: List[Dict]) -> List[str]:
        """
        استخراج اليوزرات غير المتاحة من النتائج
        
        Args:
            results (List[Dict]): نتائج التحقق
        
        Returns:
            List[str]: قائمة اليوزرات غير المتاحة
        """
        return [r['username'] for r in results if r['available'] is False]


# مثال على الاستخدام
async def main():
    checker = InstagramChecker()
    
    # قائمة اختبار
    test_usernames = ['test', 'abcd', 'xyz1', 'user']
    
    print("جاري التحقق من اليوزرات...")
    results = await checker.check_batch_usernames(test_usernames)
    
    print("\nالنتائج:")
    for result in results:
        status = "متاح ✓" if result['available'] else "غير متاح ✗" if result['available'] is False else "خطأ ⚠"
        print(f"  {result['username']}: {status}")
    
    available = checker.get_available_usernames(results)
    print(f"\nاليوزرات المتاحة: {available}")


if __name__ == "__main__":
    asyncio.run(main())
