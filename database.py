"""
نظام إدارة قاعدة البيانات
يقوم بحفظ واسترجاع اليوزرات المتاحة من قاعدة بيانات SQLite
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
import os


class DatabaseManager:
    """فئة لإدارة قاعدة البيانات"""
    
    def __init__(self, db_path: str = "instagram_usernames.db"):
        """
        تهيئة مدير قاعدة البيانات
        
        Args:
            db_path (str): مسار ملف قاعدة البيانات
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات إذا لم تكن موجودة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول اليوزرات المتاحة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS available_usernames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        
        # جدول سجل الفحوصات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS check_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                available BOOLEAN NOT NULL,
                status_code INTEGER,
                error_message TEXT,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الإحصائيات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_checked INTEGER DEFAULT 0,
                total_available INTEGER DEFAULT 0,
                total_unavailable INTEGER DEFAULT 0,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_available_username(self, username: str, notes: str = None) -> bool:
        """
        إضافة يوزر متاح إلى قاعدة البيانات
        
        Args:
            username (str): اليوزر المراد إضافته
            notes (str): ملاحظات إضافية
        
        Returns:
            bool: True إذا تم الإضافة بنجاح، False إذا كان اليوزر موجود بالفعل
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            conn.execute('PRAGMA journal_mode=WAL')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO available_usernames (username, status, notes)
                VALUES (?, ?, ?)
            ''', (username, 'available', notes))
            
            conn.commit()
            conn.close()
            return True
        
        except sqlite3.IntegrityError:
            # اليوزر موجود بالفعل
            return False
        except Exception as e:
            print(f"خطأ في إضافة اليوزر: {e}")
            return False
    
    def add_multiple_usernames(self, usernames: List[str]) -> Dict[str, int]:
        """
        إضافة عدة يوزرات متاحة
        
        Args:
            usernames (List[str]): قائمة اليوزرات
        
        Returns:
            Dict: إحصائيات الإضافة
        """
        added = 0
        duplicates = 0
        
        for username in usernames:
            if self.add_available_username(username):
                added += 1
            else:
                duplicates += 1
        
        return {
            'added': added,
            'duplicates': duplicates,
            'total': len(usernames)
        }
    
    def add_check_history(self, username: str, available: bool, 
                         status_code: int = None, error_message: str = None):
        """
        إضافة سجل فحص
        
        Args:
            username (str): اليوزر
            available (bool): هل اليوزر متاح
            status_code (int): رمز الحالة HTTP
            error_message (str): رسالة الخطأ إن وجدت
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO check_history (username, available, status_code, error_message)
                VALUES (?, ?, ?, ?)
            ''', (username, available, status_code, error_message))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"خطأ في إضافة السجل: {e}")
    
    def get_all_available_usernames(self) -> List[str]:
        """
        الحصول على جميع اليوزرات المتاحة
        
        Returns:
            List[str]: قائمة اليوزرات المتاحة
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT username FROM available_usernames ORDER BY created_at DESC')
            usernames = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return usernames
        except Exception as e:
            print(f"خطأ في استرجاع اليوزرات: {e}")
            return []
    
    def get_available_usernames_count(self) -> int:
        """
        الحصول على عدد اليوزرات المتاحة
        
        Returns:
            int: عدد اليوزرات
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM available_usernames')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
        except Exception as e:
            print(f"خطأ في عد اليوزرات: {e}")
            return 0
    
    def get_recent_available_usernames(self, limit: int = 10) -> List[str]:
        """
        الحصول على أحدث اليوزرات المتاحة
        
        Args:
            limit (int): عدد النتائج (افتراضي: 10)
        
        Returns:
            List[str]: قائمة اليوزرات
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username FROM available_usernames 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            usernames = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return usernames
        except Exception as e:
            print(f"خطأ في استرجاع اليوزرات الحديثة: {e}")
            return []
    
    def check_username_exists(self, username: str) -> bool:
        """
        التحقق من وجود يوزر في قاعدة البيانات
        
        Args:
            username (str): اليوزر المراد البحث عنه
        
        Returns:
            bool: True إذا كان موجود
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT 1 FROM available_usernames WHERE username = ?', (username,))
            exists = cursor.fetchone() is not None
            
            conn.close()
            return exists
        except Exception as e:
            print(f"خطأ في البحث: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        الحصول على إحصائيات قاعدة البيانات
        
        Returns:
            Dict: الإحصائيات
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # عدد اليوزرات المتاحة
            cursor.execute('SELECT COUNT(*) FROM available_usernames')
            total_available = cursor.fetchone()[0]
            
            # عدد الفحوصات الكلي
            cursor.execute('SELECT COUNT(*) FROM check_history')
            total_checks = cursor.fetchone()[0]
            
            # عدد اليوزرات المتاحة من السجل
            cursor.execute('SELECT COUNT(*) FROM check_history WHERE available = 1')
            available_from_history = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_available_usernames': total_available,
                'total_checks': total_checks,
                'available_from_checks': available_from_history
            }
        except Exception as e:
            print(f"خطأ في الحصول على الإحصائيات: {e}")
            return {}
    
    def delete_username(self, username: str) -> bool:
        """
        حذف يوزر من قاعدة البيانات
        
        Args:
            username (str): اليوزر المراد حذفه
        
        Returns:
            bool: True إذا تم الحذف
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM available_usernames WHERE username = ?', (username,))
            conn.commit()
            conn.close()
            
            return cursor.rowcount > 0
        except Exception as e:
            print(f"خطأ في حذف اليوزر: {e}")
            return False
    
    def clear_database(self):
        """مسح جميع البيانات من قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM available_usernames')
            cursor.execute('DELETE FROM check_history')
            
            conn.commit()
            conn.close()
            print("تم مسح قاعدة البيانات بنجاح")
        except Exception as e:
            print(f"خطأ في مسح قاعدة البيانات: {e}")


# مثال على الاستخدام
if __name__ == "__main__":
    db = DatabaseManager()
    
    # إضافة بعض اليوزرات
    test_usernames = ['abcd', 'xyz1', 'test', 'user']
    result = db.add_multiple_usernames(test_usernames)
    print(f"نتائج الإضافة: {result}")
    
    # الحصول على جميع اليوزرات
    all_usernames = db.get_all_available_usernames()
    print(f"\nجميع اليوزرات: {all_usernames}")
    
    # الحصول على الإحصائيات
    stats = db.get_statistics()
    print(f"\nالإحصائيات: {stats}")
