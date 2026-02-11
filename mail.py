import os
import smtplib
import ssl
import json
import html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app


def _h(s):
    return html.escape(str(s)) if s else '—'


def send_order_email(order):
    config = current_app.config

    sender = config['MAIL_USERNAME']
    recipient = config['MAIL_RECIPIENT']
    password = config['MAIL_PASSWORD']
    server_addr = config['MAIL_SERVER']
    port = config['MAIL_PORT']

    current_app.logger.info(f'Sending email: from={sender}, to={recipient}, server={server_addr}:{port}, ssl={config["MAIL_USE_SSL"]}')

    if not password:
        current_app.logger.error('MAIL_PASSWORD is empty -- cannot send email')
        return False

    msg = MIMEMultipart('mixed')
    msg['Subject'] = f'Новый заказ #{order.id} — Печати7'
    msg['From'] = sender
    msg['To'] = recipient

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #2563EB; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">Новый заказ #{order.id}</h1>
        </div>
        <div style="padding: 20px; background: #f9fafb;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #e5e7eb;">Имя:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{_h(order.name)}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #e5e7eb;">Телефон:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{_h(order.phone)}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #e5e7eb;">Email:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{_h(order.email or '—')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #e5e7eb;">Товар:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{_h(order.product.name if order.product else (order.order_type or '—'))}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #e5e7eb;">Макет:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{_h(order.layout.name if order.layout else '—')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #e5e7eb;">Оснастка:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{_h(order.price_option.osnastka_type if order.price_option else (order.osnastka or '—'))}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #e5e7eb;">Итого:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{str(int(order.total_price)) + ' руб.' if order.total_price else '—'}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #e5e7eb;">Сообщение:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{_h(order.message or '—')}</td>
                </tr>
            """
    if getattr(order, 'needs_delivery', False):
        html += f"""
                <tr>
                    <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #e5e7eb;">Доставка:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">Да (+500 руб.)</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #e5e7eb;">Дата и время доставки:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{_h(order.delivery_datetime or '—')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #e5e7eb;">Адрес доставки:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{_h(order.delivery_address or '—')}</td>
                </tr>
            """
    if order.params_json:
        try:
            params = json.loads(order.params_json)
            if params:
                params_str = ', '.join(f'{_h(k)}: {_h(v)}' for k, v in params.items() if v)
                html += f"""
                <tr>
                    <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #e5e7eb;">Параметры:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{params_str}</td>
                </tr>
            """
        except (json.JSONDecodeError, TypeError):
            pass
    html += """
            </table>
        </div>
        <div style="padding: 15px; text-align: center; color: #6b7280; font-size: 12px;">
            Печати7 — Автоматическое уведомление
        </div>
    </body>
    </html>
    """

    body = MIMEMultipart('alternative')
    body.attach(MIMEText(html, 'html'))
    msg.attach(body)

    upload_folder = config.get('UPLOAD_FOLDER', '')
    for file_field in [order.file_path, getattr(order, 'file_path_step3', '') or '']:
        if file_field:
            file_path = os.path.join(upload_folder, file_field) if upload_folder else file_field
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'rb') as fp:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(fp.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment', filename=file_field)
                    msg.attach(part)
                except Exception as e:
                    current_app.logger.warning(f'Could not attach file {file_field}: {e}')

    try:
        context = ssl.create_default_context()
        if config['MAIL_USE_SSL']:
            with smtplib.SMTP_SSL(server_addr, port, context=context) as server:
                server.login(sender, password)
                server.sendmail(sender, recipient, msg.as_string())
        else:
            with smtplib.SMTP(server_addr, port) as server:
                server.starttls(context=context)
                server.login(sender, password)
                server.sendmail(sender, recipient, msg.as_string())
        current_app.logger.info(f'Email sent successfully for order #{order.id}')
        return True
    except Exception as e:
        current_app.logger.error(f'Email send FAILED for order #{order.id}: {type(e).__name__}: {e}')
        return False
