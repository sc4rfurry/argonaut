# /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from typing import TextIO, Optional
from enum import Enum
import logging
from logging.handlers import RotatingFileHandler


class LogLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


class ArgonautLogger:
    """
    A logger for Argonaut applications.

    Attributes:
        name (str): The name of the logger.
        level (LogLevel): The logging level.
        output (TextIO): The output stream for logging.
    """

    def __init__(
        self, name: str, level: LogLevel = LogLevel.INFO, output: TextIO = sys.stdout
    ):
        self.name = name
        self.level = level
        self.output = output
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(output)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _log(self, level: LogLevel, message: str, *args, **kwargs):
        if level.value >= self.level.value:
            log_method = getattr(self.logger, level.name.lower())
            log_method(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        self._log(LogLevel.DEBUG, message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self._log(LogLevel.INFO, message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self._log(LogLevel.WARNING, message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self._log(LogLevel.ERROR, message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        self._log(LogLevel.CRITICAL, message, *args, **kwargs)

    def set_level(self, level: LogLevel):
        self.level = level
        self.logger.setLevel(level.value * 10)

    def set_output(self, output: TextIO):
        self.output = output
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        handler = logging.StreamHandler(output)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def set_output_file(
        self, filename: str, max_bytes: int = 10_000_000, backup_count: int = 5
    ):
        file_handler = RotatingFileHandler(
            filename, maxBytes=max_bytes, backupCount=backup_count
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log(self, message: str, level: str):
        log_level = getattr(LogLevel, level.upper(), LogLevel.INFO)
        self._log(log_level, message)

    @classmethod
    def get_logger(
        cls, name: str, level: LogLevel = LogLevel.INFO, output: Optional[TextIO] = None
    ) -> "ArgonautLogger":
        return cls(name, level, output or sys.stdout)


class ArgonautLoggerFactory:
    _loggers = {}

    @classmethod
    def get_logger(
        cls, name: str, level: LogLevel = LogLevel.INFO, output: Optional[TextIO] = None
    ) -> ArgonautLogger:
        if name not in cls._loggers:
            cls._loggers[name] = ArgonautLogger(name, level, output or sys.stdout)
        return cls._loggers[name]

    @classmethod
    def set_global_level(cls, level: LogLevel):
        for logger in cls._loggers.values():
            logger.set_level(level)

    @classmethod
    def set_global_output(cls, output: TextIO):
        for logger in cls._loggers.values():
            logger.set_output(output)
