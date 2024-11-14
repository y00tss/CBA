import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logger:
    def __init__(self, name: str, level: int = logging.INFO,
                 log_to_file: bool = False, log_dir: str = 'services/logger/logs',
                 filename: str = 'app.log'):
        """
        :param name:
        :param level:
        :param log_to_file:
        :param log_dir:
        :param filename:
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

        if log_to_file:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            file_path = Path(log_dir) / filename
            file_handler = RotatingFileHandler(
                file_path, maxBytes=5 * 1024 * 1024, backupCount=5
            )
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger
