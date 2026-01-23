"""
ملف اختبار مكونات البوت
يختبر جميع الوحدات بشكل منفصل
"""

import asyncio
from username_generator import UsernameGenerator
from instagram_checker import InstagramChecker
from database import DatabaseManager


def test_username_generator():
    """اختبار مولد اليوزرات"""
    print("=" * 50)
    print("🧪 اختبار مولد اليوزرات")
    print("=" * 50)
    
    generator = UsernameGenerator()
    
    # اختبار 1: إنشاء يوزر واحد
    print("\n✓ اختبار 1: إنشاء يوزر واحد")
    single = generator.generate_single_username()
    print(f"  اليوزر المُنشأ: {single}")
    print(f"  الطول: {len(single)} أحرف")
    assert len(single) == 4, "اليوزر يجب أن يكون 4 أحرف"
    print("  ✅ النتيجة: نجح")
    
    # اختبار 2: إنشاء عدة يوزرات
    print("\n✓ اختبار 2: إنشاء 10 يوزرات")
    multiple = generator.generate_multiple_usernames(10)
    print(f"  عدد اليوزرات: {len(multiple)}")
    print(f"  اليوزرات: {', '.join(multiple)}")
    assert len(multiple) == 10, "يجب أن تكون 10 يوزرات"
    assert len(set(multiple)) == 10, "لا يجب أن تكون هناك تكرارات"
    print("  ✅ النتيجة: نجح")
    
    # اختبار 3: التحقق من صيغة اليوزرات
    print("\n✓ اختبار 3: التحقق من صيغة اليوزرات")
    for username in multiple:
        assert len(username) == 4, f"اليوزر {username} ليس 4 أحرف"
        assert username.islower() or username.isdigit() or '_' in username, \
            f"اليوزر {username} يحتوي على أحرف غير مسموحة"
    print("  ✅ جميع اليوزرات صحيحة الصيغة")
    
    print("\n✅ جميع اختبارات مولد اليوزرات نجحت!\n")


async def test_instagram_checker():
    """اختبار مدقق إنستجرام"""
    print("=" * 50)
    print("🧪 اختبار مدقق إنستجرام")
    print("=" * 50)
    
    checker = InstagramChecker()
    
    # اختبار 1: فحص يوزر واحد
    print("\n✓ اختبار 1: فحص يوزر واحد")
    result = await checker.check_username_availability('testuser123456')
    print(f"  اليوزر: {result['username']}")
    print(f"  متاح: {result['available']}")
    print(f"  رمز الحالة: {result['status_code']}")
    assert 'username' in result, "النتيجة يجب أن تحتوي على username"
    assert 'available' in result, "النتيجة يجب أن تحتوي على available"
    print("  ✅ النتيجة: نجح")
    
    # اختبار 2: فحص عدة يوزرات
    print("\n✓ اختبار 2: فحص عدة يوزرات")
    test_usernames = ['abcd1234', 'xyz9999', 'test5678']
    results = await checker.check_multiple_usernames(test_usernames)
    print(f"  عدد النتائج: {len(results)}")
    assert len(results) == len(test_usernames), "يجب أن تكون النتائج بنفس عدد اليوزرات"
    print("  ✅ النتيجة: نجح")
    
    # اختبار 3: استخراج اليوزرات المتاحة
    print("\n✓ اختبار 3: استخراج اليوزرات المتاحة")
    available = checker.get_available_usernames(results)
    unavailable = checker.get_unavailable_usernames(results)
    print(f"  المتاحة: {len(available)}")
    print(f"  غير المتاحة: {len(unavailable)}")
    print(f"  المتاحة: {available}")
    print("  ✅ النتيجة: نجح")
    
    print("\n✅ جميع اختبارات مدقق إنستجرام نجحت!\n")


def test_database():
    """اختبار قاعدة البيانات"""
    print("=" * 50)
    print("🧪 اختبار قاعدة البيانات")
    print("=" * 50)
    
    # استخدام قاعدة بيانات اختبار منفصلة
    db = DatabaseManager("test_instagram_usernames.db")
    
    # اختبار 1: إضافة يوزر واحد
    print("\n✓ اختبار 1: إضافة يوزر واحد")
    result = db.add_available_username('test')
    print(f"  تم الإضافة: {result}")
    assert result is True, "يجب أن تكون الإضافة ناجحة"
    print("  ✅ النتيجة: نجح")
    
    # اختبار 2: محاولة إضافة يوزر مكرر
    print("\n✓ اختبار 2: محاولة إضافة يوزر مكرر")
    result = db.add_available_username('test')
    print(f"  تم الإضافة: {result}")
    assert result is False, "يجب أن تفشل إضافة يوزر مكرر"
    print("  ✅ النتيجة: نجح")
    
    # اختبار 3: إضافة عدة يوزرات
    print("\n✓ اختبار 3: إضافة عدة يوزرات")
    test_usernames = ['abcd', 'xyz1', 'user', 'test2']
    result = db.add_multiple_usernames(test_usernames)
    print(f"  النتائج: {result}")
    assert result['added'] > 0, "يجب أن تكون هناك إضافات"
    print("  ✅ النتيجة: نجح")
    
    # اختبار 4: الحصول على جميع اليوزرات
    print("\n✓ اختبار 4: الحصول على جميع اليوزرات")
    all_usernames = db.get_all_available_usernames()
    print(f"  عدد اليوزرات: {len(all_usernames)}")
    print(f"  اليوزرات: {all_usernames}")
    assert len(all_usernames) > 0, "يجب أن تكون هناك يوزرات"
    print("  ✅ النتيجة: نجح")
    
    # اختبار 5: عد اليوزرات
    print("\n✓ اختبار 5: عد اليوزرات")
    count = db.get_available_usernames_count()
    print(f"  العدد: {count}")
    assert count > 0, "يجب أن يكون هناك يوزرات"
    print("  ✅ النتيجة: نجح")
    
    # اختبار 6: الحصول على أحدث اليوزرات
    print("\n✓ اختبار 6: الحصول على أحدث اليوزرات")
    recent = db.get_recent_available_usernames(2)
    print(f"  عدد النتائج: {len(recent)}")
    print(f"  اليوزرات: {recent}")
    print("  ✅ النتيجة: نجح")
    
    # اختبار 7: التحقق من وجود يوزر
    print("\n✓ اختبار 7: التحقق من وجود يوزر")
    exists = db.check_username_exists('test')
    print(f"  موجود: {exists}")
    assert exists is True, "يجب أن يكون اليوزر موجود"
    print("  ✅ النتيجة: نجح")
    
    # اختبار 8: الحصول على الإحصائيات
    print("\n✓ اختبار 8: الحصول على الإحصائيات")
    stats = db.get_statistics()
    print(f"  الإحصائيات: {stats}")
    assert 'total_available_usernames' in stats, "يجب أن تحتوي على total_available_usernames"
    print("  ✅ النتيجة: نجح")
    
    # اختبار 9: إضافة سجل فحص
    print("\n✓ اختبار 9: إضافة سجل فحص")
    db.add_check_history('testuser', True, 404, None)
    print("  تم إضافة السجل")
    print("  ✅ النتيجة: نجح")
    
    # اختبار 10: حذف يوزر
    print("\n✓ اختبار 10: حذف يوزر")
    result = db.delete_username('test2')
    print(f"  تم الحذف: {result}")
    print("  ✅ النتيجة: نجح")
    
    print("\n✅ جميع اختبارات قاعدة البيانات نجحت!\n")


async def run_all_tests():
    """تشغيل جميع الاختبارات"""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║" + " " * 10 + "🧪 بدء اختبار مكونات البوت" + " " * 12 + "║")
    print("╚" + "=" * 48 + "╝")
    print()
    
    try:
        # اختبار مولد اليوزرات
        test_username_generator()
        
        # اختبار مدقق إنستجرام
        await test_instagram_checker()
        
        # اختبار قاعدة البيانات
        test_database()
        
        print("\n")
        print("╔" + "=" * 48 + "╗")
        print("║" + " " * 15 + "✅ جميع الاختبارات نجحت!" + " " * 8 + "║")
        print("╚" + "=" * 48 + "╝")
        print()
        
    except AssertionError as e:
        print(f"\n❌ فشل الاختبار: {e}\n")
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
