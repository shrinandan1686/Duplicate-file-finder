"""
Logging configuration for the Duplicate File Finder application.
Provides both file and console logging with rotation support.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(name: str = "DuplicateFinder", log_dir: str = "logs") -> logging.Logger:
    """
    Configure and return a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_dir: Directory to store log files
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger
    
    # File handler with rotation (10 MB max, keep 5 backups)
    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler (only warnings and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    # Format for both handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "DuplicateFinder") -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


# Convenience function for deletion logging
def log_deletion(file_path: str, method: str, status: str, error: str = None):
    """
    Log a deletion operation with structured information.
    
    Args:
        file_path: Path of the file being deleted
        method: 'recycle_bin' or 'hard_delete'
        status: 'success' or 'failed'
        error: Optional error message if status is 'failed'
    """
    logger = get_logger()
    log_msg = f"Deletion - File: {file_path} | Method: {method} | Status: {status}"
    
    if error:
        log_msg += f" | Error: {error}"
        logger.error(log_msg)
    else:
        logger.info(log_msg)
