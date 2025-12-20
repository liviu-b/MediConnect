"""
Advanced Logging Configuration
Structured logging with correlation IDs and log levels
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
import uuid
from contextvars import ContextVar

# Context variable for request ID tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    Makes logs easier to parse and analyze.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data['request_id'] = request_id
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for console output.
    Makes logs easier to read during development.
    """
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    json_logs: bool = False,
    log_file: str = None
):
    """
    Setup application logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Use JSON format for logs
        log_file: Optional file path for logs
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if json_logs:
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
    
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)
    
    # Suppress noisy loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds extra context to log messages.
    """
    
    def process(self, msg, kwargs):
        # Add request ID to all logs
        request_id = request_id_var.get()
        if request_id:
            kwargs['extra'] = kwargs.get('extra', {})
            kwargs['extra']['request_id'] = request_id
        return msg, kwargs


def log_execution_time(func):
    """
    Decorator to log function execution time.
    
    Usage:
        @log_execution_time
        async def slow_function():
            await asyncio.sleep(1)
    """
    import functools
    import time
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                f"{func.__name__} executed in {execution_time:.3f}s",
                extra={'execution_time': execution_time}
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.3f}s: {e}",
                extra={'execution_time': execution_time, 'error': str(e)}
            )
            raise
    
    return wrapper
