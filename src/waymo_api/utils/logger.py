import sys
import logging
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler

def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10_485_760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
	# Create logger
	logger = logging.getLogger("waymo_client")
	logger.setLevel(log_level.upper())

	# Prevent adding handlers multiple times
	if logger.handlers:
		return logger
			
	# Create formatters
	detailed_formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
	console_formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%H:%M:%S')

	# Console handler
	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setFormatter(console_formatter)
	logger.addHandler(console_handler)

	# File handler (if log_file specified)
	if log_file:
		log_path = Path(log_file)
		log_path.parent.mkdir(parents=True, exist_ok=True)

		file_handler = RotatingFileHandler(
			log_path,
			maxBytes=max_bytes,
			backupCount=backup_count
		)
		file_handler.setFormatter(detailed_formatter)
		logger.addHandler(file_handler)
	return logger

def get_logger(name: str) -> logging.Logger:
	return logging.getLogger(f"waymo_client.{name}")