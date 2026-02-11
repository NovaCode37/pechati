import smtplib
import ssl
import os
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), encoding='utf-8')

MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.yandex.ru')
MAIL_PORT = os.getenv('MAIL_PORT', '465')
MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'True').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
MAIL_RECIPIENT = os.getenv('MAIL_RECIPIENT', '')

try:
    MAIL_PORT = int(MAIL_PORT)
except (TypeError, ValueError):
    MAIL_PORT = 465

print('=== Проверка почты ===')
print('Сервер:', MAIL_SERVER)
print('Порт:', MAIL_PORT, '| SSL:', MAIL_USE_SSL)
print('Отправитель:', MAIL_USERNAME)
print('Получатель:', MAIL_RECIPIENT)
print('Пароль задан:', 'да' if MAIL_PASSWORD else 'НЕТ')
print()

if not MAIL_PASSWORD:
    print('ОШИБКА: В .env нет MAIL_PASSWORD')
    sys.exit(1)

msg = f"""From: {MAIL_USERNAME}
To: {MAIL_RECIPIENT}
Subject: Test Pechati7

Testovoe pis'mo. Esli poluchili - pochta rabotaet.
"""

def try_send(port, use_ssl):
    context = ssl.create_default_context()
    if use_ssl:
        server = smtplib.SMTP_SSL(MAIL_SERVER, port, context=context, timeout=15)
    else:
        server = smtplib.SMTP(MAIL_SERVER, port, timeout=15)
        server.starttls(context=context)
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    server.sendmail(MAIL_USERNAME, MAIL_RECIPIENT, msg)
    server.quit()

last_error = None
for port, use_ssl in [(MAIL_PORT, MAIL_USE_SSL), (465, True), (587, False)]:
    try:
        print(f'Пробуем {MAIL_SERVER}:{port} SSL={use_ssl}...', end=' ')
        try_send(port, use_ssl)
        print('OK')
        print()
        print('Pismo otpravleno. Proverte pochtu i papku Spam.')
        sys.exit(0)
    except Exception as e:
        print('fail')
        last_error = e

print()
print('Oshibka:', type(last_error).__name__, last_error)
print()
print('--- Esli Yandex ne rabotaet, poprobujte Gmail ---')
print('1. Google Account -> Bezopasnost -> 2-etapnaya proverka (vkl.)')
print('2. Paroli prilozheniy -> Sozdat, vybrat "Pochta", skopirovat parol')
print('3. V .env ukazat:')
print('   MAIL_SERVER=smtp.gmail.com')
print('   MAIL_PORT=587')
print('   MAIL_USE_SSL=False')
print('   MAIL_USERNAME=vash@gmail.com')
print('   MAIL_PASSWORD=parol_prilozheniya')
print('   MAIL_RECIPIENT=vash@gmail.com')
print('4. Zapustit: python test_email.py')
sys.exit(1)
