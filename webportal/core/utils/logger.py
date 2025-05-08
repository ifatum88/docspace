import logging
import os

from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

def get_logger(name:str, log_dir:str, level: int = logging.INFO) -> logging.Logger:
    """
    Возвращает настроенный логгер с ежедневной ротацией файлов с именем в формате YYYY-MM-DD.log
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)

        # Построим абсолютный путь к папке логов
        os.makedirs(log_dir, exist_ok=True)

        # Формируем имя файла по дате
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(log_dir, f"{date_str}.log")

        # Создаем обработчик с ротацией по времени
        handler = TimedRotatingFileHandler(
            log_path,
            when="midnight",     # ротация каждый день
            interval=1,
            backupCount=30,
            encoding="utf-8",
            utc=True
        )

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s [%(pathname)s:%(lineno)d]')
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger