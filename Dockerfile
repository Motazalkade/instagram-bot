FROM python:3.11-slim

WORKDIR /app

# تثبيت المكتبات النظام المطلوبة
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت المكتبات Python
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الملفات
COPY . .

# تشغيل البوت
CMD ["python", "telegram_bot.py"]
