import logging
import sys
from typing import ClassVar


class StructuredFormatter(logging.Formatter):
    """Custom formatter for clean, aligned, and colored console output."""

    FORMAT: ClassVar[str] = '%(asctime)s | %(levelname)-17s | %(name)-30s | %(message)s'

    COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: '\033[90m',  # Gray
        logging.INFO: '\033[36m',  # Cyan
        logging.WARNING: '\033[33m',  # Yellow
        logging.ERROR: '\033[31m',  # Red
        logging.CRITICAL: '\033[1;31m',  # Bold Red
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname  # Storing the original level to prevent mutation

        color = self.COLORS.get(record.levelno, self.RESET)
        record.levelname = f'{color}{original_levelname}{self.RESET}'

        formatter = logging.Formatter(self.FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
        formatted_message = formatter.format(record)

        record.levelname = original_levelname

        return formatted_message


def configure_logging(log_level: int = logging.INFO) -> None:
    """Configures global logging for both API and Engine packages."""

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredFormatter())

    logging.basicConfig(
        level=log_level,
        handlers=[console_handler],
        force=True,  # Overrides any existing configuration
    )

    # Uvicorn usually sets up its own formatters, this overwrites them.
    for logger_name in ('uvicorn', 'uvicorn.error', 'uvicorn.access', 'fastapi'):
        target_logger = logging.getLogger(logger_name)
        target_logger.handlers = [console_handler]
        target_logger.propagate = False
