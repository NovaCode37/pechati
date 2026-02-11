========================================
НАСТРОЙКА ПОЧТЫ ДЛЯ ЗАКАЗОВ
========================================

Если письма с заказами не приходят, чаще всего Яндекс не принимает пароль.
Используйте Gmail — обычно работает с первого раза.

--- ВАРИАНТ 1: GMAIL (рекомендуется) ---

1. Включите двухфакторную аутентификацию в Google:
   https://myaccount.google.com/security

2. Создайте пароль приложения:
   https://myaccount.google.com/apppasswords
   (Выберите «Почта» и «Другое устройство», скопируйте пароль)

3. В файле .env замените настройки почты на:

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_SSL=False
MAIL_USERNAME=ваш_логин@gmail.com
MAIL_PASSWORD=пароль_приложения_из_шага_2
MAIL_RECIPIENT=ваш_логин@gmail.com

4. Запустите проверку: python test_email.py

--- ВАРИАНТ 2: MAIL.RU ---

1. mail.ru -> Настройки -> Пароль и безопасность -> Пароль для почты (создать)

2. В .env укажите:

MAIL_SERVER=smtp.mail.ru
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=ваш_логин@mail.ru
MAIL_PASSWORD=пароль_для_почты
MAIL_RECIPIENT=ваш_логин@mail.ru

3. Запустите: python test_email.py

--- ВАРИАНТ 3: YANDEX (если заработает) ---

MAIL_SERVER=smtp.yandex.ru
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=ваш@yandex.ru
MAIL_PASSWORD=пароль_приложения_из_id.yandex.ru
MAIL_RECIPIENT=ваш@yandex.ru

========================================
