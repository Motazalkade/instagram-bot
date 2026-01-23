"""
نظام إنشاء اليوزرات الرباعية العشوائية
يقوم بإنشاء يوزرات عشوائية مكونة من 4 أحرف للإنستجرام
"""

import random
import string
from typing import List


class UsernameGenerator:
    """فئة لإنشاء يوزرات عشوائية رباعية"""
    
    def __init__(self):
        """تهيئة مولد اليوزرات"""
        # الأحرف المسموحة في اليوزرات (أحرف صغيرة وأرقام وشرطة سفلية)
        self.allowed_chars = string.ascii_lowercase + string.digits + '_'
    
    def generate_single_username(self) -> str:
        """
        إنشاء يوزر واحد عشوائي مكون من 4 أحرف
        
        Returns:
            str: يوزر عشوائي مكون من 4 أحرف
        """
        username = ''.join(random.choice(self.allowed_chars) for _ in range(4))
        return username
    
    def generate_multiple_usernames(self, count: int = 10) -> List[str]:
        """
        إنشاء عدة يوزرات عشوائية
        
        Args:
            count (int): عدد اليوزرات المراد إنشاؤها (افتراضي: 10)
        
        Returns:
            List[str]: قائمة بالـ usernames المُنشأة
        """
        usernames = []
        seen = set()
        
        # التأكد من عدم تكرار اليوزرات
        while len(usernames) < count:
            username = self.generate_single_username()
            if username not in seen:
                usernames.append(username)
                seen.add(username)
        
        return usernames
    
    def generate_batch_usernames(self, batch_size: int = 100) -> List[str]:
        """
        إنشاء دفعة كبيرة من اليوزرات
        
        Args:
            batch_size (int): حجم الدفعة (افتراضي: 100)
        
        Returns:
            List[str]: قائمة بـ usernames المُنشأة
        """
        return self.generate_multiple_usernames(batch_size)


# مثال على الاستخدام
if __name__ == "__main__":
    generator = UsernameGenerator()
    
    # إنشاء يوزر واحد
    single = generator.generate_single_username()
    print(f"يوزر واحد: {single}")
    
    # إنشاء 10 يوزرات
    multiple = generator.generate_multiple_usernames(10)
    print(f"\n10 يوزرات:")
    for username in multiple:
        print(f"  - {username}")
