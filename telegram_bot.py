"""
بوت تلجرام للتحقق من توفر اليوزرات على إنستجرام
يوفر واجهة تفاعلية بالأزرار
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from telegram.constants import ParseMode

from username_generator import UsernameGenerator
from instagram_checker import InstagramChecker
from database import DatabaseManager

# تفعيل السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# حالات المحادثة
MAIN_MENU, GENERATE_COUNT, CHECKING = range(3)

# تهيئة الأدوات
generator = UsernameGenerator()
checker = InstagramChecker()
db = DatabaseManager()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالج أمر البداية"""
    user = update.effective_user
    
    welcome_message = f"""
👋 مرحباً بك {user.first_name}!

أنا بوت متخصص في التحقق من توفر اليوزرات الرباعية على إنستجرام.

يمكنني:
✅ إنشاء يوزرات عشوائية رباعية
✅ التحقق من توفرها على إنستجرام
✅ حفظ اليوزرات المتاحة في قاعدة بيانات
✅ عرض الإحصائيات

اختر من الخيارات أدناه للبدء:
    """
    
    keyboard = [
        [InlineKeyboardButton("🔄 إنشاء والتحقق", callback_data='generate_check')],
        [InlineKeyboardButton("📊 عرض الإحصائيات", callback_data='statistics')],
        [InlineKeyboardButton("📋 اليوزرات المتاحة", callback_data='show_available')],
        [InlineKeyboardButton("ℹ️ معلومات", callback_data='info')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    return MAIN_MENU


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالج نقرات الأزرار"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'generate_check':
        await query.edit_message_text(
            text="كم عدد اليوزرات التي تريد إنشاؤها والتحقق منها؟\n\n(أدخل رقماً من 1 إلى 50)",
            reply_markup=None
        )
        return GENERATE_COUNT
    
    elif query.data == 'statistics':
        stats = db.get_statistics()
        stats_message = f"""
📊 الإحصائيات:

📌 إجمالي اليوزرات المتاحة: {stats.get('total_available_usernames', 0)}
🔍 إجمالي الفحوصات: {stats.get('total_checks', 0)}
✅ اليوزرات المتاحة من الفحوصات: {stats.get('available_from_checks', 0)}
        """
        
        keyboard = [
            [InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data='back_to_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(stats_message, reply_markup=reply_markup)
        return MAIN_MENU
    
    elif query.data == 'show_available':
        usernames = db.get_recent_available_usernames(20)
        
        if usernames:
            usernames_text = '\n'.join([f"• {u}" for u in usernames])
            message = f"📋 أحدث {len(usernames)} يوزرات متاحة:\n\n{usernames_text}"
        else:
            message = "لا توجد يوزرات متاحة حتى الآن."
        
        keyboard = [
            [InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data='back_to_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
        return MAIN_MENU
    
    elif query.data == 'info':
        info_message = """
ℹ️ معلومات عن البوت:

🤖 **الميزات:**
• إنشاء يوزرات عشوائية مكونة من 4 أحرف
• التحقق من توفر اليوزرات على إنستجرام
• حفظ اليوزرات المتاحة في قاعدة بيانات
• عرض الإحصائيات والتقارير

⚙️ **كيفية الاستخدام:**
1. اختر "إنشاء والتحقق"
2. أدخل عدد اليوزرات المراد فحصها
3. سيقوم البوت بإنشاء والتحقق من اليوزرات
4. سيتم حفظ اليوزرات المتاحة تلقائياً

⏱️ **ملاحظة:**
قد يستغرق الفحص بعض الوقت حسب عدد اليوزرات.
        """
        
        keyboard = [
            [InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data='back_to_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(info_message, reply_markup=reply_markup)
        return MAIN_MENU
    
    elif query.data == 'back_to_main':
        await start(update, context)
        return MAIN_MENU


async def handle_count_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالج إدخال عدد اليوزرات"""
    try:
        count = int(update.message.text)
        
        if count < 1 or count > 50:
            await update.message.reply_text(
                "❌ الرجاء إدخال رقم بين 1 و 50"
            )
            return GENERATE_COUNT
        
        # حفظ العدد في السياق
        context.user_data['count'] = count
        
        # إرسال رسالة الانتظار
        wait_message = await update.message.reply_text(
            f"⏳ جاري إنشاء والتحقق من {count} يوزرات...\n\nقد يستغرق هذا بعض الوقت."
        )
        
        # إنشاء اليوزرات
        usernames = generator.generate_multiple_usernames(count)
        
        # تحديث الرسالة
        await wait_message.edit_text(
            f"🔍 جاري التحقق من {count} يوزرات على إنستجرام...\n\nهذا قد يستغرق دقيقة أو أكثر."
        )
        
        # التحقق من اليوزرات
        results = await checker.check_batch_usernames(usernames)
        
        # استخراج اليوزرات المتاحة
        available_usernames = checker.get_available_usernames(results)
        
        # حفظ اليوزرات المتاحة في قاعدة البيانات
        if available_usernames:
            db_result = db.add_multiple_usernames(available_usernames)
            
            # حفظ سجل الفحوصات
            for result in results:
                db.add_check_history(
                    result['username'],
                    result['available'],
                    result['status_code'],
                    result['error']
                )
        
        # تحضير رسالة النتائج
        unavailable = checker.get_unavailable_usernames(results)
        
        results_message = f"""
✅ **انتهى الفحص!**

📊 النتائج:
• إجمالي الفحوصات: {len(results)}
• ✅ اليوزرات المتاحة: {len(available_usernames)}
• ❌ اليوزرات المستخدمة: {len(unavailable)}

🎉 اليوزرات المتاحة الجديدة:
        """
        
        if available_usernames:
            for username in available_usernames[:10]:  # عرض أول 10 فقط
                results_message += f"\n• @{username}"
            
            if len(available_usernames) > 10:
                results_message += f"\n... و {len(available_usernames) - 10} يوزرات أخرى"
        else:
            results_message += "\nللأسف لم نجد أي يوزرات متاحة في هذه المحاولة."
        
        # إرسال النتائج
        keyboard = [
            [InlineKeyboardButton("🔄 محاولة أخرى", callback_data='generate_check')],
            [InlineKeyboardButton("📋 عرض جميع المتاحة", callback_data='show_available')],
            [InlineKeyboardButton("⬅️ القائمة الرئيسية", callback_data='back_to_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await wait_message.edit_text(results_message, reply_markup=reply_markup)
        
        return MAIN_MENU
    
    except ValueError:
        await update.message.reply_text(
            "❌ الرجاء إدخال رقم صحيح (من 1 إلى 50)"
        )
        return GENERATE_COUNT


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر المساعدة"""
    help_text = """
/start - بدء البوت
/help - عرض المساعدة
/stats - عرض الإحصائيات
/available - عرض اليوزرات المتاحة
    """
    await update.message.reply_text(help_text)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر الإحصائيات"""
    stats = db.get_statistics()
    stats_message = f"""
📊 الإحصائيات:

📌 إجمالي اليوزرات المتاحة: {stats.get('total_available_usernames', 0)}
🔍 إجمالي الفحوصات: {stats.get('total_checks', 0)}
✅ اليوزرات المتاحة من الفحوصات: {stats.get('available_from_checks', 0)}
    """
    await update.message.reply_text(stats_message)


async def available_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر عرض اليوزرات المتاحة"""
    usernames = db.get_recent_available_usernames(20)
    
    if usernames:
        usernames_text = '\n'.join([f"• @{u}" for u in usernames])
        message = f"📋 أحدث {len(usernames)} يوزرات متاحة:\n\n{usernames_text}"
    else:
        message = "لا توجد يوزرات متاحة حتى الآن."
    
    await update.message.reply_text(message)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الأخطاء"""
    logger.error(f"حدث خطأ: {context.error}")


def main():
    """تشغيل البوت"""
    # استبدل بـ token الخاص بك
    TOKEN = "8593625858:AAGyBE-IlZu_guOLhGfb_rQf6TlSAG1u9bM"
    
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("available", available_command))
    
    # إضافة معالج نقرات الأزرار
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # إضافة معالج إدخال النصوص
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_count_input))
    
    # إضافة معالج الأخطاء
    application.add_error_handler(error_handler)
    
    # بدء البوت
    print("🤖 البوت يعمل الآن...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
