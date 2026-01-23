# 📚 شرح الكود والعمليات

شرح تفصيلي لكيفية عمل البوت والعمليات الداخلية.

## 🏗️ معمارية البوت

```
┌─────────────────────────────────────────────┐
│         بوت تلجرام (Telegram Bot)          │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │     واجهة المستخدم (UI)              │  │
│  │  - أزرار تفاعلية                     │  │
│  │  - رسائل نصية                        │  │
│  └──────────────────────────────────────┘  │
│                    │                        │
│                    ▼                        │
│  ┌──────────────────────────────────────┐  │
│  │   معالج الأوامر والأزرار              │  │
│  │  - معالجة /start, /help              │  │
│  │  - معالجة نقرات الأزرار              │  │
│  └──────────────────────────────────────┘  │
│                    │                        │
│     ┌──────────────┼──────────────┐        │
│     ▼              ▼              ▼        │
│  ┌────────┐  ┌──────────┐  ┌──────────┐   │
│  │ مولد   │  │  مدقق    │  │ قاعدة    │   │
│  │ اليوزر │  │ إنستجرام │  │ البيانات │   │
│  └────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────┘
```

## 📝 شرح المكونات الرئيسية

### 1️⃣ username_generator.py - مولد اليوزرات

#### الفئة: `UsernameGenerator`

```python
class UsernameGenerator:
    def __init__(self):
        # الأحرف المسموحة: أحرف صغيرة + أرقام + شرطة سفلية
        self.allowed_chars = string.ascii_lowercase + string.digits + '_'
```

#### الدوال الرئيسية:

**1. `generate_single_username()`**
```python
def generate_single_username(self) -> str:
    # اختيار 4 أحرف عشوائية من الأحرف المسموحة
    username = ''.join(random.choice(self.allowed_chars) for _ in range(4))
    return username
```

**الخطوات:**
1. استخدام `random.choice()` لاختيار حرف عشوائي
2. تكرار العملية 4 مرات
3. دمج الأحرف في نص واحد

**مثال:**
```
الأحرف المتاحة: a-z, 0-9, _
الاختيار العشوائي: 'a', 'b', 'c', 'd'
النتيجة: 'abcd'
```

**2. `generate_multiple_usernames(count)`**
```python
def generate_multiple_usernames(self, count: int = 10) -> List[str]:
    usernames = []
    seen = set()  # لتجنب التكرار
    
    while len(usernames) < count:
        username = self.generate_single_username()
        if username not in seen:  # تحقق من عدم التكرار
            usernames.append(username)
            seen.add(username)
    
    return usernames
```

**الخطوات:**
1. إنشاء قائمة فارغة لحفظ اليوزرات
2. إنشاء مجموعة (set) لتتبع اليوزرات المُنشأة
3. حلقة تكرار حتى نصل للعدد المطلوب
4. التحقق من عدم تكرار اليوزر
5. إضافة اليوزر الجديد

---

### 2️⃣ instagram_checker.py - مدقق إنستجرام

#### الفئة: `InstagramChecker`

```python
class InstagramChecker:
    def __init__(self):
        # رابط الملف الشخصي على إنستجرام
        # مثال: https://www.instagram.com/username/
        self.instagram_api_url = "https://www.instagram.com/api/v1/users/search/"
        self.delay = 0.5  # تأخير بين الطلبات
```

#### الدوال الرئيسية:

**1. `check_username_availability(username)` - فحص يوزر واحد**

```python
async def check_username_availability(self, username: str) -> Dict:
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://www.instagram.com/{username}/"
            
            async with session.get(url, headers=self.headers, timeout=10) as response:
                # إذا كان الرد 404 = اليوزر متاح
                if response.status == 404:
                    return {
                        'username': username,
                        'available': True,
                        'status_code': 404,
                        'error': None
                    }
                # إذا كان الرد 200 = اليوزر مستخدم
                elif response.status == 200:
                    return {
                        'username': username,
                        'available': False,
                        'status_code': 200,
                        'error': 'اليوزر مستخدم بالفعل'
                    }
    except Exception as e:
        return {
            'username': username,
            'available': None,
            'status_code': None,
            'error': str(e)
        }
```

**آلية العمل:**
```
1. إرسال طلب HTTP GET إلى صفحة اليوزر
   ↓
2. فحص رمز الحالة (Status Code):
   ├─ 404 → اليوزر متاح ✅
   ├─ 200 → اليوزر مستخدم ❌
   └─ غير ذلك → خطأ ⚠️
   ↓
3. إرجاع النتيجة مع التفاصيل
```

**2. `check_batch_usernames(usernames, batch_size)` - فحص متزامن**

```python
async def check_batch_usernames(self, usernames: List[str], batch_size: int = 5):
    results = []
    
    # معالجة اليوزرات على دفعات
    for i in range(0, len(usernames), batch_size):
        batch = usernames[i:i + batch_size]
        
        # فحص الدفعة بشكل متزامن
        batch_results = await asyncio.gather(
            *[self.check_username_availability(username) for username in batch]
        )
        results.extend(batch_results)
        
        # تأخير بين الدفعات
        if i + batch_size < len(usernames):
            await asyncio.sleep(1)
    
    return results
```

**آلية العمل:**
```
اليوزرات: [user1, user2, user3, user4, user5, user6]
حجم الدفعة: 2

الدفعة 1: [user1, user2] → فحص متزامن
         ↓
الدفعة 2: [user3, user4] → فحص متزامن (بعد 1 ثانية)
         ↓
الدفعة 3: [user5, user6] → فحص متزامن (بعد 1 ثانية)
```

**فوائد الفحص المتزامن:**
- ⚡ أسرع من الفحص المتسلسل
- 🔄 معالجة عدة يوزرات في نفس الوقت
- 🛡️ تأخيرات بين الدفعات لتجنب الحظر

---

### 3️⃣ database.py - إدارة قاعدة البيانات

#### الفئة: `DatabaseManager`

```python
class DatabaseManager:
    def __init__(self, db_path: str = "instagram_usernames.db"):
        self.db_path = db_path
        self.init_database()  # إنشاء الجداول
```

#### الجداول:

**جدول 1: available_usernames**
```sql
CREATE TABLE available_usernames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
)
```

**جدول 2: check_history**
```sql
CREATE TABLE check_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    available BOOLEAN NOT NULL,
    status_code INTEGER,
    error_message TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### الدوال الرئيسية:

**1. `add_available_username(username)`**

```python
def add_available_username(self, username: str, notes: str = None) -> bool:
    try:
        conn = sqlite3.connect(self.db_path, timeout=10)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO available_usernames (username, status, notes)
            VALUES (?, ?, ?)
        ''', (username, 'available', notes))
        
        conn.commit()
        conn.close()
        return True
    
    except sqlite3.IntegrityError:
        # اليوزر موجود بالفعل (UNIQUE constraint)
        return False
```

**آلية العمل:**
```
1. فتح الاتصال بقاعدة البيانات
2. إنشاء cursor للتنفيذ
3. تنفيذ أمر INSERT مع معاملات آمنة (?)
4. حفظ التغييرات (commit)
5. إغلاق الاتصال
6. إرجاع True إذا نجح
```

**2. `get_statistics()`**

```python
def get_statistics(self) -> Dict:
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    # عد اليوزرات المتاحة
    cursor.execute('SELECT COUNT(*) FROM available_usernames')
    total_available = cursor.fetchone()[0]
    
    # عد الفحوصات الكلي
    cursor.execute('SELECT COUNT(*) FROM check_history')
    total_checks = cursor.fetchone()[0]
    
    # عد اليوزرات المتاحة من السجل
    cursor.execute('SELECT COUNT(*) FROM check_history WHERE available = 1')
    available_from_history = cursor.fetchone()[0]
    
    return {
        'total_available_usernames': total_available,
        'total_checks': total_checks,
        'available_from_checks': available_from_history
    }
```

---

### 4️⃣ telegram_bot.py - بوت تلجرام

#### معالجات الأوامر:

**1. معالج `/start`**

```python
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # إنشاء لوحة مفاتيح بأزرار
    keyboard = [
        [InlineKeyboardButton("🔄 إنشاء والتحقق", callback_data='generate_check')],
        [InlineKeyboardButton("📊 عرض الإحصائيات", callback_data='statistics')],
        # ... أزرار أخرى
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # إرسال الرسالة مع الأزرار
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    return MAIN_MENU
```

**آلية العمل:**
```
المستخدم يرسل /start
         ↓
معالج start يتم تنفيذه
         ↓
إنشاء لوحة مفاتيح بأزرار
         ↓
إرسال رسالة مع الأزرار
         ↓
انتظار نقرة على زر
```

**2. معالج نقرات الأزرار**

```python
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()  # إيقاف رمز التحميل
    
    if query.data == 'generate_check':
        # طلب من المستخدم إدخال العدد
        await query.edit_message_text(
            text="كم عدد اليوزرات التي تريد إنشاؤها والتحقق منها؟"
        )
        return GENERATE_COUNT
    
    elif query.data == 'statistics':
        # الحصول على الإحصائيات من قاعدة البيانات
        stats = db.get_statistics()
        # عرض الإحصائيات
        await query.edit_message_text(stats_message)
        return MAIN_MENU
```

**3. معالج إدخال العدد**

```python
async def handle_count_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        count = int(update.message.text)
        
        # التحقق من الحد الأدنى والأقصى
        if count < 1 or count > 50:
            await update.message.reply_text("❌ الرجاء إدخال رقم بين 1 و 50")
            return GENERATE_COUNT
        
        # إنشاء اليوزرات
        usernames = generator.generate_multiple_usernames(count)
        
        # التحقق من اليوزرات
        results = await checker.check_batch_usernames(usernames)
        
        # استخراج اليوزرات المتاحة
        available_usernames = checker.get_available_usernames(results)
        
        # حفظ في قاعدة البيانات
        if available_usernames:
            db.add_multiple_usernames(available_usernames)
        
        # إرسال النتائج
        await update.message.reply_text(results_message)
        
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
        return GENERATE_COUNT
```

#### تدفق العملية الكاملة:

```
المستخدم يرسل /start
         ↓
عرض القائمة الرئيسية مع الأزرار
         ↓
المستخدم ينقر على "🔄 إنشاء والتحقق"
         ↓
البوت يطلب عدد اليوزرات
         ↓
المستخدم يرسل رقم (مثل: 5)
         ↓
البوت ينشئ 5 يوزرات عشوائية
         ↓
البوت يفحص كل يوزر على إنستجرام
         ↓
البوت يحفظ اليوزرات المتاحة في قاعدة البيانات
         ↓
البوت يعرض النتائج للمستخدم
         ↓
المستخدم يمكنه اختيار عملية أخرى
```

---

## 🔄 تدفق البيانات

```
┌──────────────────────────────────────────────────────┐
│                    المستخدم                          │
└──────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────┐
│              بوت تلجرام (معالج الأوامر)              │
└──────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────┐
│           مولد اليوزرات (إنشاء 5 يوزرات)             │
│  النتيجة: ['abcd', 'xyz1', 'user', 'test', 'qwer']  │
└──────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────┐
│         مدقق إنستجرام (فحص كل يوزر)                 │
│  النتيجة: [                                          │
│    {username: 'abcd', available: True},             │
│    {username: 'xyz1', available: False},            │
│    ...                                              │
│  ]                                                  │
└──────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────┐
│      قاعدة البيانات (حفظ اليوزرات المتاحة)           │
│  - إضافة اليوزرات المتاحة إلى جدول available_usernames│
│  - إضافة سجل لكل فحص إلى جدول check_history        │
└──────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────┐
│              عرض النتائج للمستخدم                     │
│  ✅ اليوزرات المتاحة: abcd, ...                      │
│  ❌ اليوزرات المستخدمة: xyz1, ...                    │
└──────────────────────────────────────────────────────┘
```

---

## 🔒 معالجة الأخطاء

### في مولد اليوزرات:
```python
# تجنب التكرار باستخدام set
if username not in seen:
    usernames.append(username)
```

### في مدقق إنستجرام:
```python
try:
    # محاولة الفحص
except asyncio.TimeoutError:
    # معالجة انتهاء المهلة الزمنية
except Exception as e:
    # معالجة أي خطأ آخر
```

### في قاعدة البيانات:
```python
try:
    # محاولة الإضافة
except sqlite3.IntegrityError:
    # اليوزر موجود بالفعل (UNIQUE constraint)
except Exception as e:
    # معالجة أي خطأ آخر
```

---

## ⚡ تحسينات الأداء

### 1. الفحص المتزامن (Async)
```python
# بدلاً من:
for username in usernames:
    result = await check(username)

# نستخدم:
results = await asyncio.gather(
    *[check(username) for username in usernames]
)
```

### 2. التأخيرات الذكية
```python
# تأخير بين الطلبات لتجنب الحظر
await asyncio.sleep(0.5)

# تأخير أطول بين الدفعات
await asyncio.sleep(1)
```

### 3. استخدام Connection Pooling
```python
# بدلاً من فتح اتصال جديد في كل مرة
# نستخدم aiohttp.ClientSession
async with aiohttp.ClientSession() as session:
    # استخدام الجلسة لعدة طلبات
```

---

## 📊 أمثلة على الاستخدام

### مثال 1: إنشاء يوزرات
```python
from username_generator import UsernameGenerator

generator = UsernameGenerator()
usernames = generator.generate_multiple_usernames(5)
# النتيجة: ['abcd', 'xyz1', 'user', 'test', 'qwer']
```

### مثال 2: فحص اليوزرات
```python
import asyncio
from instagram_checker import InstagramChecker

async def main():
    checker = InstagramChecker()
    results = await checker.check_batch_usernames(['abcd', 'xyz1'])
    print(results)

asyncio.run(main())
```

### مثال 3: حفظ في قاعدة البيانات
```python
from database import DatabaseManager

db = DatabaseManager()
db.add_available_username('abcd')
db.add_multiple_usernames(['xyz1', 'user'])

stats = db.get_statistics()
print(stats)
```

---

## 🎯 الخلاصة

البوت يعمل على ثلاث مراحل رئيسية:

1. **الإنشاء**: مولد اليوزرات ينشئ يوزرات عشوائية
2. **التحقق**: مدقق إنستجرام يفحص كل يوزر
3. **الحفظ**: قاعدة البيانات تحفظ النتائج

كل مكون مستقل ويمكن استخدامه بشكل منفصل، مما يجعل الكود مرن وسهل الصيانة.
