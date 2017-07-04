import logging

logger = logging.getLogger('vk-raid-defender')
logger.setLevel(logging.INFO)
terminal_logger = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s.%(msecs).03d] %(message)s", datefmt="%H:%M:%S")
terminal_logger.setFormatter(formatter)
logger.addHandler(terminal_logger)
logger.propagate = False
