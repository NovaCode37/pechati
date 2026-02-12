import time
import uuid
import os
from functools import wraps
from flask import request, abort


RATE_WINDOW = 60

_rate_storage = {}


def allowed_file(filename, allowed_extensions):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in allowed_extensions


def safe_save_upload(file_storage, upload_folder, allowed_extensions):
    if not file_storage or not getattr(file_storage, 'filename', None) or not file_storage.filename.strip():
        return None
    if not allowed_file(file_storage.filename, allowed_extensions):
        return None
    ext = file_storage.filename.rsplit('.', 1)[-1].lower()
    safe_name = f'{uuid.uuid4().hex}.{ext}'
    path = os.path.join(upload_folder, safe_name)
    try:
        file_storage.save(path)
        return safe_name
    except (OSError, PermissionError):
        return None


def truncate_str(value, max_len):
    if value is None:
        return ''
    s = str(value).strip()
    return s[:max_len] if len(s) > max_len else s


def apply_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://api-maps.yandex.ru; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "frame-src 'self' https://yandex.ru https://api-maps.yandex.ru; "
        "frame-ancestors 'self';"
    )
    return response


def _rate_key(prefix):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()
    return f"{prefix}:{ip}"


def check_rate_limit(prefix, max_requests):
    key = _rate_key(prefix)
    now = time.time()
    if key not in _rate_storage:
        _rate_storage[key] = (1, now)
        return True
    count, start = _rate_storage[key]
    if now - start > RATE_WINDOW:
        _rate_storage[key] = (1, now)
        return True
    if count >= max_requests:
        return False
    _rate_storage[key] = (count + 1, start)
    return True


def rate_limit(prefix, max_requests):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not check_rate_limit(prefix, max_requests):
                abort(429)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def layout_belongs_to_product(layout_id, product_id, layouts_query):
    if not layout_id:
        return False
    try:
        lid = int(layout_id)
    except (ValueError, TypeError):
        return False
    return any(l.id == lid for l in layouts_query)


def price_option_belongs_to_product(price_option_id, product_id, price_options_query):
    if not price_option_id:
        return False
    try:
        pid = int(price_option_id)
    except (ValueError, TypeError):
        return False
    return any(p.id == pid for p in price_options_query)
