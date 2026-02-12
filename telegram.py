import os
import json
import requests
from flask import current_app


def send_order_telegram(order):
    token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '')

    if not token or not chat_id:
        current_app.logger.warning('TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set — skipping Telegram notification')
        return False

    product_name = order.product.name if order.product else (order.order_type or '—')
    layout_name = order.layout.name if order.layout else '—'
    osnastka = order.price_option.osnastka_type if order.price_option else (order.osnastka or '—')
    total = f'{int(order.total_price)} руб.' if order.total_price else '—'

    lines = [
        f'🆕 *Новый заказ \\#{order.id}*',
        '',
        f'👤 *Имя:* {_esc(order.name)}',
        f'📞 *Телефон:* {_esc(order.phone)}',
    ]
    if order.email:
        lines.append(f'📧 *Email:* {_esc(order.email)}')
    lines += [
        f'📦 *Товар:* {_esc(product_name)}',
        f'🎨 *Макет:* {_esc(layout_name)}',
        f'🔧 *Оснастка:* {_esc(osnastka)}',
        f'💰 *Итого:* {_esc(total)}',
    ]
    if order.message:
        lines.append(f'💬 *Сообщение:* {_esc(order.message)}')

    if getattr(order, 'needs_delivery', False):
        lines.append(f'🚚 *Доставка:* Да \\(\\+500 руб\\.\\)')
        if order.delivery_datetime:
            lines.append(f'📅 *Дата доставки:* {_esc(str(order.delivery_datetime))}')
        if order.delivery_address:
            lines.append(f'📍 *Адрес:* {_esc(order.delivery_address)}')

    if order.params_json:
        try:
            params = json.loads(order.params_json)
            if params:
                params_str = ', '.join(f'{_esc(k)}: {_esc(v)}' for k, v in params.items() if v)
                lines.append(f'⚙️ *Параметры:* {params_str}')
        except (json.JSONDecodeError, TypeError):
            pass

    text = '\n'.join(lines)

    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'MarkdownV2',
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            current_app.logger.info(f'Telegram notification sent for order #{order.id}')
            return True
        else:
            current_app.logger.error(f'Telegram API error for order #{order.id}: {resp.status_code} {resp.text}')
            return False
    except Exception as e:
        current_app.logger.error(f'Telegram send FAILED for order #{order.id}: {type(e).__name__}: {e}')
        return False


def _esc(s):
    """Escape special characters for MarkdownV2."""
    if not s:
        return '—'
    s = str(s)
    for ch in r'\_*[]()~`>#+-=|{}.!':
        s = s.replace(ch, f'\\{ch}')
    return s
