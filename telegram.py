import os
import json
import requests
from flask import current_app


PARAM_TRANSLATIONS = {
    'inn': 'ИНН',
    'ogrn': 'ОГРН',
    'ogrnip': 'ОГРНИП',
    'kpp': 'КПП',
    'city': 'Город',
    'company_name': 'Название компании',
    'company': 'Компания',
    'name': 'Имя',
    'full_name': 'ФИО',
    'fio': 'ФИО',
    'director': 'Директор',
    'director_name': 'ФИО директора',
    'phone': 'Телефон',
    'email': 'Email',
    'address': 'Адрес',
    'message': 'Сообщение',
    'comment': 'Комментарий',
    'text': 'Текст',
    'position': 'Должность',
    'speciality': 'Специальность',
    'license': 'Номер лицензии',
    'license_number': 'Номер лицензии',
    'region': 'Регион',
    'stamp_text': 'Текст печати',
    'bottom_text': 'Нижний текст',
    'top_text': 'Верхний текст',
    'center_text': 'Центральный текст',
    'middle_text': 'Средний текст',
}


def _translate_key(key):
    k = key.strip().lower().replace(' ', '_')
    return PARAM_TRANSLATIONS.get(k, key)


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
                translated = [f'{_esc(_translate_key(k))}: {_esc(v)}' for k, v in params.items() if v]
                if translated:
                    lines.append(f'⚙️ *Параметры:*')
                    for item in translated:
                        lines.append(f'    {item}')
        except (json.JSONDecodeError, TypeError):
            pass

    text = '\n'.join(lines)

    api_base = f'https://api.telegram.org/bot{token}'

    try:
        resp = requests.post(f'{api_base}/sendMessage', json={
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'MarkdownV2',
        }, timeout=10)
        if resp.status_code == 200:
            current_app.logger.info(f'Telegram notification sent for order #{order.id}')
        else:
            current_app.logger.error(f'Telegram API error for order #{order.id}: {resp.status_code} {resp.text}')
    except Exception as e:
        current_app.logger.error(f'Telegram send FAILED for order #{order.id}: {type(e).__name__}: {e}')

    upload_folder = current_app.config.get('UPLOAD_FOLDER', '')
    for file_field in [order.file_path, getattr(order, 'file_path_step3', '') or '']:
        if not file_field:
            continue
        full_path = os.path.join(upload_folder, file_field) if upload_folder else file_field
        if not os.path.isfile(full_path):
            continue
        try:
            with open(full_path, 'rb') as f:
                resp = requests.post(
                    f'{api_base}/sendDocument',
                    data={'chat_id': chat_id, 'caption': f'📎 Файл к заказу #{order.id}'},
                    files={'document': (file_field, f)},
                    timeout=30,
                )
            if resp.status_code == 200:
                current_app.logger.info(f'Telegram file {file_field} sent for order #{order.id}')
            else:
                current_app.logger.error(f'Telegram file send error: {resp.status_code} {resp.text}')
        except Exception as e:
            current_app.logger.error(f'Telegram file send FAILED {file_field}: {type(e).__name__}: {e}')

    return True


def _esc(s):
    """Escape special characters for MarkdownV2."""
    if not s:
        return '—'
    s = str(s)
    for ch in r'\_*[]()~`>#+-=|{}.!':
        s = s.replace(ch, f'\\{ch}')
    return s
