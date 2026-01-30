"""
Logging configuration
"""
import logging
import sys

# Create logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
LOGGER.addHandler(console_handler)
LOGGER.addHandler(file_handler)