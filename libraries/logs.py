import logging
from pathlib import Path
from datetime import datetime

class GVMLoggingFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        if not datefmt:
            return super().formatTime(record, datefmt=datefmt)

        return datetime.fromtimestamp(record.created).astimezone().strftime(datefmt)

class GVMLogger(logging.Logger):
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    WARN = WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    FATAL = CRITICAL
    UNKNOWN = -1

    _levelToName = {
        NOTSET: "NOTSET",
        DEBUG: "DEBUG",
        INFO: "INFO",
        WARNING: "WARNING",
        WARN: "WARN",
        ERROR: "ERROR",
        CRITICAL: "CRITICAL",
        FATAL: "FATAL",
    }

    _nameToLevel = {
        "NOTSET": NOTSET,
        "DEBUG": DEBUG,
        "INFO": INFO,
        "WARNING": WARNING,
        "WARN": WARN,
        "ERROR": ERROR,
        "CRITICAL": CRITICAL,
        "FATAL": FATAL,
    }
    
    def __init__(
            self, 
            name: str, 
            file_path: Path | str,
            level: int | str = DEBUG,
            formatter: GVMLoggingFormatter = GVMLoggingFormatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S.%f %z"),
            ) -> None:
        super().__init__(name, level)
        self.file_path: Path = Path(file_path)
        self.formatter = formatter
        self.__setup_logger()
        
    def __setup_logger(self):
        log_path = self.file_path.parent
        log_path.mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(self.file_path)
        handler.setFormatter(self.formatter)
        self.addHandler(handler)
        self.propagate = False
        
    def write_log(self, msg: str, level: int = DEBUG):
        if level == self.NOTSET:
            self.debug(f"[NOTSET] {msg}")
        elif level == self.DEBUG:
            self.debug(msg)
        elif level == self.INFO:
            self.info(msg)
        elif level == self.WARN:
            self.warning(msg)
        elif level == self.ERROR:
            self.error(msg)
        elif level == self.FATAL:
            self.critical(msg)
        else:
            # UNKNOWN
            self.warning(f"[UNKNOWN LEVEL {level}] {msg}")

# Cara penggunaan:
if __name__ == "__main__":
    logger = GVMLogger("gvm_script", Path("/home/com/openvas/gvm-script/logs/gvm_script.log"))
    
    logger.write_log("This is a notset level message", GVMLogger.NOTSET)
    logger.write_log("This is a debug level message", GVMLogger.DEBUG)
    logger.write_log("This is an info level message", GVMLogger.INFO)
    logger.write_log("This is a warning level message", GVMLogger.WARN)
    logger.write_log("This is an error level message", GVMLogger.ERROR)
    logger.write_log("This is a fatal level message", GVMLogger.FATAL)
    logger.write_log("This is an unknown level message", 999)  # Level yang tidak dikenal
    
    print("Logging complete")