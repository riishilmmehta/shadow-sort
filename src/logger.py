import logging
import sys

def setup_logger(name: str, verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
