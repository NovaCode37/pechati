# Публикация на GitHub и хостинг

## Что уже сделано

- В репозитории **нет** файлов с секретами: `.env`, `.env.txt`, база `pechati5.db` в `.gitignore`.
- Есть `.env.example` — список переменных для продакшена (без реальных паролей).
- Создан первый коммит, можно пушить на GitHub.

## Как отправить проект на GitHub

### 1. Создайте репозиторий на GitHub

1. Зайдите на [github.com](https://github.com), войдите в аккаунт.
2. Нажмите **New repository** (или **+** → New repository).
3. Имя, например: `pechati7`.
4. **Не** ставьте галочки "Add a README" и "Add .gitignore" — репозиторий должен быть пустым.
5. Нажмите **Create repository**.

### 2. Привяжите проект и запушьте

В папке проекта выполните (подставьте **свой** логин и имя репозитория):

```bash
cd C:\Users\golub\pechati5

git remote add origin https://github.com/ВАШ_ЛОГИН/pechati7.git
git branch -M main
git push -u origin main
```

При запросе логина/пароля: используйте **Personal Access Token** (не пароль от аккаунта).  
Создать токен: GitHub → Settings → Developer settings → Personal access tokens → Generate new token (права `repo`).

### 3. (По желанию) Укажите своё имя для коммитов

```bash
git config user.name "Ваше Имя"
git config user.email "ваш-email@example.com"
```

## Хостинг после пуша

После того как код на GitHub:

- **Vercel / Netlify** — для статики; для Flask нужен serverless (Python runtime).
- **Python-хостинг** (Railway, Render, PythonAnywhere, Beget, Timeweb и т.п.):
  - Клонируют репозиторий.
  - Указывают команду запуска, например: `gunicorn -w 1 -b 0.0.0.0:8000 app:app`.
  - В настройках окружения добавляют переменные из `.env.example` (SECRET_KEY, MAIL_*, ADMIN_*, DATABASE_URL при использовании PostgreSQL).

На сервере создайте файл `.env` из `.env.example` и заполните реальными значениями; сам `.env` в репозиторий не попадает.
