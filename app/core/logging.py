import logging
import sys


def setup_logging() -> None:
    """Настраивает логирование для всего приложения."""
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    )
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    # Снижаем уровень логирования у "болтливых" сторонних библиотек
    logging.getLogger("passlib").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
