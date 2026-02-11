# Печати7 — Сайт по продаже печатей и штампов

Современный веб-сайт для компании по изготовлению печатей и штампов с админ-панелью.

## Стек технологий

- **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login
- **Database**: SQLite
- **Frontend**: Jinja2 + TailwindCSS (CDN) + Font Awesome
- **Email**: Яндекс.Почта SMTP

## Быстрый старт

### 1. Установка зависимостей

```bash
cd pechati5
pip install -r requirements.txt
```

### 2. Настройка

Отредактируйте файл `.env`:

```env
SECRET_KEY=ваш-секретный-ключ
MAIL_SERVER=smtp.yandex.ru
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=ваша-почта@yandex.ru
MAIL_PASSWORD=пароль-приложения
MAIL_RECIPIENT=куда-приходят-заказы@email.com
```

**Как получить пароль приложения Яндекс:**
1. Зайдите на https://id.yandex.ru/security/app-passwords
2. Создайте пароль приложения для «Почты»
3. Скопируйте пароль в `MAIL_PASSWORD`

### 3. Заполнение базы данных

```bash
python seed.py
```

### 4. Запуск

```bash
python app.py
```

Сайт будет доступен по адресу: **http://localhost:5000**

## Админ-панель

- URL: http://localhost:5000/admin
- Логин и пароль задаются в `.env` переменными `ADMIN_USERNAME` и `ADMIN_PASSWORD` или при первом запуске `seed.py`.

### Возможности админ-панели:

- Обзор (статистика по заказам)
- Управление категориями (добавление, редактирование, удаление)
- Управление товарами и ценами
- Просмотр и обработка заказов (фильтрация по статусу)
- Настройки сайта (телефон, email, адрес, режим работы)

## Структура проекта

```
pechati5/
├── app.py              # Главный файл приложения (все маршруты)
├── config.py           # Конфигурация
├── models.py           # Модели базы данных
├── forms.py            # WTForms формы
├── mail.py             # Отправка email через Яндекс
├── seed.py             # Начальные данные
├── requirements.txt    # Зависимости Python
├── .env                # Переменные окружения (не коммитить!)
├── templates/          # HTML-шаблоны
│   ├── base.html       # Базовый шаблон
│   ├── index.html      # Главная
│   ├── catalog.html    # Каталог категории
│   ├── prices.html     # Прайс-лист
│   ├── order.html      # Форма заказа
│   ├── contacts.html   # Контакты
│   ├── delivery.html   # Доставка
│   ├── about.html      # О компании
│   └── admin/          # Шаблоны админки
└── static/
    ├── css/custom.css  # Кастомные стили
    ├── js/main.js      # JavaScript
    ├── images/         # Изображения
    └── uploads/        # Загруженные файлы
```

## Страницы сайта

| URL | Описание |
|-----|----------|
| `/` | Главная страница |
| `/catalog/<slug>` | Каталог категории |
| `/prices` | Прайс-лист |
| `/order` | Форма заказа |
| `/contacts` | Контакты |
| `/delivery` | Доставка |
| `/about` | О компании |
| `/admin` | Админ-панель |
