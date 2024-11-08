import logging

def get_logger(name='my_logger', level=logging.DEBUG):
    # Create a logger instance
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add formatter to console handler
    ch.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(ch)

    return logger

# Get the logger instance
logger = get_logger(name='logger')

# Example usage
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')