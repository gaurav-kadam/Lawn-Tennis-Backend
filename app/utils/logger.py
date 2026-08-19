import logging
import os
from logging.handlers import RotatingFileHandler

if not os.path.exists("logs"):
    os.mkdir("logs")

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

file_handler = RotatingFileHandler("logs/app.log", maxBytes=1024 * 1024 * 5, backupCount=5)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
