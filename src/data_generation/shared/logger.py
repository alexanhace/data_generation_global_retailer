import logging 
from logging.handlers import RotatingFileHandler
from pathlib import Path
from data_generation.shared.paths import PROJECT_ROOT

def setup_logger(
        name='data_generation',
        log_dir=PROJECT_ROOT / 'output' / 'logs',
        level=logging.INFO,
        max_bytes=2_000_000,
        backup_count=7,
):
    """Configure logging to write to both console and a rotating log file.

    Args:
        name:           Root logger name [default: 'data_generation]']
        log_dir:        Directory for log files [default: 'output/logs']
        level:          Logging level [default: INFO]
        max_bytes:      Max log file size before rotation [default: 2MB]
        backup_count:   Number of backup log files to keep [default: 7]
    
    Returns:
        Configured logger instance
    """
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    log_file = log_dir_path / f"{name}.log"

    #Define a shared format
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )

    #File handler - rotates after max_bytes, keeps backup_count files
    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    #Console handler - so you still see output in the terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logger initialized | file={log_file.resolve()} | level={logging.getLevelName(level)}")

    return logger