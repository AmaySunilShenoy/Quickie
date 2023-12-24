from logbook import Logger, FileHandler
from logbook.compat import redirect_logging

redirect_logging()

# Create logbook handlers with file locking
action_log_handler = FileHandler('action.log', level='INFO', bubble=True, delay=True)
performance_log_handler = FileHandler('performance.log', level='DEBUG', bubble=True, delay=True)

# Create loggers
action_logger = Logger('action')
performance_logger = Logger('performance')

# Add handlers to loggers
action_logger.handlers.append(action_log_handler)
performance_logger.handlers.append(performance_log_handler)
