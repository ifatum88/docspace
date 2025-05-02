import logging
import os

from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from config import Config

def get_logger(name: str = Config.APP_NAME, log_dir: str = Config.LOG_DIR, level: int = logging.INFO) -> logging.Logger:
    """
    Возвращает настроенный логгер с ежедневной ротацией файлов с именем в формате YYYY-MM-DD.log
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)

        # Построим абсолютный путь к папке логов
        log_folder_path = os.path.join(Config.BASE_DIR, log_dir)
        os.makedirs(log_folder_path, exist_ok=True)

        # Формируем имя файла по дате
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(log_folder_path, f"{date_str}.log")

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