import humanize
import html

from datetime import datetime, timezone
from flask import Flask
from email.utils import parsedate_to_datetime

def register_filters(app: Flask):


    @app.template_filter('datetime')
    def format_datetime(value, format='%d.%m.%Y %H:%M:%S'):
        """
        Преобразует значение в красивую дату:
        - если это datetime — форматирует
        - если это строка в ISO или RFC 1123 — конвертирует и форматирует
        - иначе возвращает как есть
        """
        if isinstance(value, datetime):
            return value.strftime(format)

        if isinstance(value, str):
            try:
                # Пробуем ISO
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime(format)
            except ValueError:
                try:
                    # Пробуем RFC 1123
                    dt = parsedate_to_datetime(value)
                    return dt.strftime(format)
                except Exception:
                    return value

        return value

    @app.template_filter('humantime')
    def humanize_time(value):
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value

        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)  # делаем offset-aware
            now = datetime.now(timezone.utc)
            return humanize.naturaltime(now - value)

        return value
    

    @app.template_filter('escape_with_newlines')
    def escape_with_newlines(value):
        if not isinstance(value, str):
            return value
        escaped = html.escape(value)
        return escaped.replace('\n', '<br>')