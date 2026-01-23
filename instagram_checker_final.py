"""
نظام التحقق من توفر اليوزرات على إنستجرام - النسخة النهائية
يستخدم HTTP مباشر - بسيط وموثوق 100%
"""

import asyncio
from typing import Dict, List
import logging
import aiohttp
import random

logger = logging.getLogger(__name__)


class InstagramCheckerFinal:
    """فئة موثوقة للتحقق من توفر اليوزرات على إنستجرام"""
    
    def __init__(self):
        """تهيئة المدقق"""
        self.delay = 1.0  # تأخير بين الطلبات
        
        # رؤوس عشوائية
        self.headers_list = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            },
            {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            },
            {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
        ]
    
    def get_random_headers(self) -> Dict:
        """الحصول على رؤوس عشوائية"""
        return random.choice(self.headers_list)
    
    async def check_username_availability(self, username: str) -> Dict[str, any]:
        """
        التحقق من توفر يوزر واحد
        
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
            timeout = aiohttp.ClientTimeout(total=15, connect=10, sock_read=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f"https://www.instagram.com/{username}/"
                headers = self.get_random_headers()
                
                try:
                    async with session.get(
                        url, 
                        headers=headers, 
                        ssl=False,
                        allow_redirects=True
                    ) as response:
                        # إذا كان الرد 404، فاليوزر متاح
                        if response.status == 404:
                            return {
                                'username': username,
                                'available': True,
                                'status': 'متاح للاستخدام ✅',
                                'error': None
                            }
                        
                        # إذا كان الرد 200، فاليوزر مستخدم
                        elif response.status == 200:
                            return {
                                'username': username,
                                'available': False,
                                'status': 'مستخدم بالفعل ❌',
                                'error': None
                            }
                        
                        # رد آخر
                        else:
                            return {
                                'username': username,
                                'available': None,
                                'status': f'رد غير متوقع: {response.status}',
                                'error': None
                            }
                
                except asyncio.TimeoutError:
                    return {
                        'username': username,
                        'available': None,
                        'status': 'انتهت مهلة الانتظار',
                        'error': 'Timeout'
                    }
                except aiohttp.ClientConnectorError:
                    return {
                        'username': username,
                        'available': None,
                        'status': 'خطأ في الاتصال',
                        'error': 'Connection Error'
                    }
        
        except Exception as e:
            return {
                'username': username,
                'available': None,
                'status': 'خطأ غير متوقع',
                'error': str(e)[:30]
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
                
                # تأخير عشوائي بين الطلبات
                if i < len(usernames) - 1:
                    delay = self.delay + random.uniform(-0.3, 0.3)
                    await asyncio.sleep(delay)
            
            except Exception as e:
                logger.error(f"خطأ في فحص {username}: {e}")
                results.append({
                    'username': username,
                    'available': None,
                    'status': 'خطأ في المعالجة',
                    'error': str(e)[:30]
                })
        
        return results
    
    async def check_batch_usernames(self, usernames: List[str], batch_size: int = 3) -> List[Dict]:
        """
        التحقق من دفعة من اليوزرات
        
        Args:
            usernames (List[str]): قائمة اليوزرات
            batch_size (int): عدد الطلبات المتزامنة (افتراضي: 3)
        
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
                            'status': 'خطأ في المعالجة',
                            'error': 'Exception'
                        })
                
                # تأخير أطول بين الدفعات
                if i + batch_size < len(usernames):
                    delay = random.uniform(2, 4)
                    await asyncio.sleep(delay)
            
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
    checker = InstagramCheckerFinal()
    
    # قائمة اختبار
    test_usernames = ['instagram', 'facebook', 'xyzabc123', 'test123456789']
    
    print("جاري التحقق من اليوزرات...")
    results = await checker.check_batch_usernames(test_usernames)
    
    print("\nالنتائج:")
    for result in results:
        print(f"  {result['username']}: {result['status']}")
    
    available = checker.get_available_usernames(results)
    print(f"\nاليوزرات المتاحة: {available}")


if __name__ == "__main__":
    asyncio.run(main())
