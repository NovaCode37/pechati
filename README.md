# Pechati — Stamp & Print Order Platform

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey)
![Type](https://img.shields.io/badge/Type-Commercial%20Project-orange)
![Deploy](https://img.shields.io/badge/Deploy-Railway%20%7C%20reg.ru-brightgreen)

A full-stack web application for a stamp and print production business. Handles product catalog, multi-step order flow, admin panel, and automated order notifications via email and Telegram. Built and deployed as a commercial freelance project.

## Features

### Application
- **Product catalog** — categories, products, layouts, price options with slug-based routing
- **Multi-step order flow** — product selection → layout → price option → file upload → confirmation
- **Admin panel** — order management, product/category CRUD, site settings (Flask-Login protected)
- **Order notifications** — instant alerts to business owner via Email and Telegram Bot
- **File uploads** — client artwork submission with strict validation

### Security Implementation
- **CSRF protection** — Flask-WTF `CSRFProtect` on all forms
- **Security headers** — full header suite applied globally via `@after_request`:
  - `Content-Security-Policy` (CSP with allowlists)
  - `Strict-Transport-Security` (HSTS, 1 year + subdomains)
  - `X-Frame-Options: SAMEORIGIN`
  - `X-Content-Type-Options: nosniff`
  - `Permissions-Policy` (blocks geolocation, microphone, camera)
  - `Referrer-Policy: strict-origin-when-cross-origin`
- **Rate limiting** — custom IP-based rate limiter (`security.py`) with configurable window/threshold, returns HTTP 429
- **Safe file uploads** — extension allowlist + UUID-based filename randomization (prevents path traversal and overwrite attacks)
- **Input sanitization** — `truncate_str()` enforces max-length on all user inputs before DB writes
- **Admin authentication** — Flask-Login with protected routes, session management

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask 3.x, SQLAlchemy, Flask-WTF, Flask-Login |
| Frontend | Jinja2 templates, TailwindCSS |
| Database | SQLite / PostgreSQL |
| Notifications | SMTP (email) + Telegram Bot API |
| Deployment | Railway, reg.ru (Passenger WSGI) |

## Project Structure

```
pechati/
├── app.py              ← routes and application factory
├── models.py           ← SQLAlchemy models (Order, Product, Category, ...)
├── forms.py            ← Flask-WTF form definitions with validators
├── security.py         ← security headers, rate limiter, safe upload, input sanitization
├── config.py           ← environment-based configuration
├── mail.py             ← SMTP order notification
├── telegram.py         ← Telegram Bot order notification
├── templates/          ← Jinja2 HTML templates
└── static/             ← CSS, JS, images
```

## Security Architecture

```
Incoming Request
      │
      ├─ CSRF token validation (Flask-WTF)
      ├─ Rate limit check (IP-based, 60s window)
      ├─ Input validation (WTForms validators)
      ├─ File upload: extension check + UUID rename
      ├─ DB write: truncated, sanitized values only
      │
Outgoing Response
      └─ Security headers applied globally (CSP, HSTS, X-Frame-Options, ...)
```

## Environment Variables

```bash
SECRET_KEY=
DATABASE_URL=
MAIL_SERVER=
MAIL_USERNAME=
MAIL_PASSWORD=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
UPLOAD_FOLDER=
```

## Running Locally

```bash
pip install -r requirements.txt
flask db upgrade
python seed.py       # optional demo data
flask run
```
