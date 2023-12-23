import logging
from logging.handlers import RotatingFileHandler

# Performance logger
performance_logger = logging.getLogger('performance_logger')
performance_handler = RotatingFileHandler('performance.log', maxBytes=10240, backupCount=10)
performance_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
performance_logger.addHandler(performance_handler)
performance_logger.setLevel(logging.INFO)

# General logger
# general_logger = logging.getLogger('general_logger')
# general_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
# general_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
# general_logger.addHandler(general_handler)
# general_logger.setLevel(logging.INFO)


# Action Logger
action_logger = logging.getLogger('action_logger')
action_handler = RotatingFileHandler('actions.log', maxBytes=10240, backupCount=10)
action_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
action_logger.addHandler(action_handler)
action_logger.setLevel(logging.INFO)
