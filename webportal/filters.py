# filters.py
from datetime import datetime, timezone
from flask import Flask
import humanize

def register_filters(app: Flask):

    @app.template_filter('datetime')
    def format_datetime(value, format='%d.%m.%Y %H:%M:%S'):
        """
        Преобразует значение в красивую дату:
        - если это datetime — форматирует
        - если это строка в ISO формате — конвертирует в datetime и форматирует
        - иначе возвращает как есть
        """
        if isinstance(value, datetime):
            return value.strftime(format)
        
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime(format)
            except ValueError:
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