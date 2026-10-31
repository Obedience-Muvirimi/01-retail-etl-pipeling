from logger_config import setup_logger

logger = setup_logger()

logger.info("Logging test successful")
logger.warning("THis is a test warning")
logger.error("This is a test error")