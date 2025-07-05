"""
日志系统模块
~~~~~~~~~~~~~~~

提供完整的API专用日志记录功能，支持服务日志和调试日志自动分离。
"""

import logging
import logging.handlers
import os
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

# --- 动态导入依赖 ---
try:
    from loguru import logger as loguru_logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False

# 尝试导入阿里云日志SDK，如果不存在则使用模拟实现
try:
    from aliyun.log import LogClient, LogItem, PutLogsRequest
    ALIYUN_LOG_AVAILABLE = True
except ImportError:
    ALIYUN_LOG_AVAILABLE = False
    class LogClient:
        def __init__(self, *args, **kwargs): pass
        def put_logs(self, request): pass
    class LogItem:
        def __init__(self): self.contents = {}
        def set_time(self, timestamp): pass
        def set_contents(self, contents): self.contents = contents
    class PutLogsRequest:
        def __init__(self, project, logstore, topic, source, logitems):
            self.project = project
            self.logstore = logstore
            self.topic = topic
            self.source = source
            self.logitems = logitems

# --- 日志接口定义 ---
class ILogger(ABC):
    """日志记录器接口，定义了所有日志实现必须遵守的方法。"""
    
    @abstractmethod
    def service_info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    def service_warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    def service_error(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        pass

    @abstractmethod
    def service_critical(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        pass
    
    @abstractmethod
    def debug_debug(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    def debug_info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    def debug_warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None:
        pass
    
    @abstractmethod
    def debug_error(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        pass

# --- 空日志实现 ---
class NullLogger(ILogger):
    """一个不执行任何操作的日志记录器，用于禁用日志功能。"""
    def service_info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: pass
    def service_warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: pass
    def service_error(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None: pass
    def service_critical(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None: pass
    def debug_debug(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: pass
    def debug_info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: pass
    def debug_warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: pass
    def debug_error(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None: pass


class BaseLogHandler(ABC):
    @abstractmethod
    def handle(self, record: logging.LogRecord) -> None:
        pass

class ConsoleHandler(BaseLogHandler):
    def __init__(self, level: int = logging.INFO):
        self.level = level
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - PID:%(process)d - %(message)s'
        )
    def handle(self, record: logging.LogRecord) -> None:
        if record.levelno >= self.level:
            print(self.formatter.format(record))

class FileHandler(BaseLogHandler):
    def __init__(self, filename: str, level: int = logging.INFO, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
        self.filename = filename
        self.level = level
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - PID:%(process)d - %(message)s'
        )
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.handler = logging.handlers.RotatingFileHandler(
            filename, maxBytes=max_bytes, backupCount=backup_count
        )
        self.handler.setLevel(level)
        self.handler.setFormatter(self.formatter)
    def handle(self, record: logging.LogRecord) -> None:
        if record.levelno >= self.level:
            self.handler.emit(record)

class AliyunLogHandler(BaseLogHandler):
    def __init__(self, project: str, logstore: str, endpoint: str, access_key_id: str, access_key_secret: str, level: int = logging.INFO):
        self.project = project
        self.logstore = logstore
        self.endpoint = endpoint
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.level = level
        self._client: Optional[LogClient] = None
    def _get_client(self) -> LogClient:
        if self._client is None:
            self._client = LogClient(
                endpoint=self.endpoint,
                accessKeyId=self.access_key_id,
                accessKeySecret=self.access_key_secret
            )
        return self._client
    def handle(self, record: logging.LogRecord) -> None:
        if not ALIYUN_LOG_AVAILABLE or record.levelno < self.level:
            return
        try:
            log_item = LogItem()
            log_item.set_time(int(time.time()))
            contents = {
                'level': logging.getLevelName(record.levelno),
                'message': record.getMessage(),
                'logger': record.name,
                'timestamp': datetime.now().isoformat(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            if record.exc_info:
                contents['exception'] = str(record.exc_info[1])
            if hasattr(record, 'extra_fields'):
                contents.update(record.extra_fields)
            log_item.set_contents(contents)
            request = PutLogsRequest(
                self.project, self.logstore, '', '', [log_item]
            )
            self._get_client().put_logs(request)
        except Exception as e:
            print(f"Failed to send log to Aliyun: {str(e)}")
            print(f"Original log: {record.getMessage()}")

# --- Loguru 实现 ---
class LoguruLogger(ILogger):
    def __init__(self, api_name: str):
        self.api_name = api_name
        self.log_dir = os.getenv('LOG_DIR', 'logs')
        os.makedirs(self.log_dir, exist_ok=True)

        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{extra[api_name]}</cyan> | <magenta>PID:{process}</magenta> - <level>{message}</level>"

        loguru_logger.remove()
        loguru_logger.add(
            sys.stdout,
            level=os.getenv('CONSOLE_LOG_LEVEL', 'INFO').upper()
        )
        loguru_logger.add(
            os.path.join(self.log_dir, f"{self.api_name}_service.log"),
            filter=lambda record: record["extra"].get("log_type") == "service",
            level=os.getenv('FILE_LOG_LEVEL', 'DEBUG').upper(),
            format=log_format, rotation="10 MB", retention="5 days", enqueue=True
        )
        loguru_logger.add(
            os.path.join(self.log_dir, f"{self.api_name}_debug.log"),
            filter=lambda record: record["extra"].get("log_type") == "debug",
            level="DEBUG",
            format=log_format, rotation="10 MB", retention="5 days", enqueue=True
        )

    def _log(self, log_type: str, level: str, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None):
        extra = {"api_name": self.api_name, "log_type": log_type}
        if extra_fields:
            extra.update(extra_fields)
        
        logger_with_context = loguru_logger.bind(**extra)
        if exc_info:
            logger_with_context.opt(exception=exc_info).log(level, message)
        else:
            logger_with_context.log(level, message)

    def service_info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: self._log("service", "INFO", message, extra_fields)
    def service_warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: self._log("service", "WARNING", message, extra_fields)
    def service_error(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None: self._log("service", "ERROR", message, extra_fields, exc_info)
    def service_critical(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None: self._log("service", "CRITICAL", message, extra_fields, exc_info)
    def debug_debug(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: self._log("debug", "DEBUG", message, extra_fields)
    def debug_info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: self._log("debug", "INFO", message, extra_fields)
    def debug_warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: self._log("debug", "WARNING", message, extra_fields)
    def debug_error(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None: self._log("debug", "ERROR", message, extra_fields, exc_info)


class _SimpleLogger:
    def __init__(self, name: str, level: int, handlers: list[BaseLogHandler]):
        self.name = name
        self.level = level
        self.handlers = handlers
    def _log(self, level: int, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        if level < self.level:
            return
        record = logging.LogRecord(
            name=self.name,
            level=level,
            pathname='',
            lineno=0,
            msg=message,
            args=(),
            exc_info=(type(exc_info), exc_info, exc_info.__traceback__) if exc_info else None
        )
        if extra_fields:
            record.extra_fields = extra_fields
        for handler in self.handlers:
            try:
                handler.handle(record)
            except Exception as e:
                print(f"Log handler error: {str(e)}")
                print(f"Original message: {message}")

# --- 内置Logging模块实现 ---
class BuiltinLogger(ILogger):
    """使用Python内置logging模块的日志记录器。"""
    def __init__(self, api_name: str, level: Optional[int] = None):
        self.api_name = api_name
        self.level = level or self._get_default_level()
        self.service_logger = self._create_logger('service')
        self.debug_logger = self._create_logger('debug', debug=True)

    def _get_default_level(self) -> int:
        level_str = os.getenv('LOG_LEVEL', 'INFO')
        return getattr(logging, level_str.upper(), logging.INFO)

    def _get_logs_dir(self) -> str:
        return os.getenv('LOG_DIR', 'logs')

    def _create_logger(self, prefix: str, debug: bool = False):
        log_file = os.path.join(self._get_logs_dir(), f"{self.api_name}{'_debug' if debug else ''}.log")
        level = logging.DEBUG if debug else self.level
        
        console_level = getattr(logging, os.getenv('CONSOLE_LOG_LEVEL', 'INFO').upper())
        file_level = getattr(logging, os.getenv('FILE_LOG_LEVEL', 'DEBUG').upper())
        max_bytes = int(os.getenv('LOG_MAX_BYTES', 10485760))
        backup_count = int(os.getenv('LOG_BACKUP_COUNT', 5))

        handlers = []
        logger_name = f"{prefix}.{self.api_name}"
        logger_obj = logging.getLogger(logger_name)
        # 只在没有handler时添加，防止重复
        if not logger_obj.hasHandlers():
            handlers.append(ConsoleHandler(level=console_level))
            handlers.append(FileHandler(log_file, level=file_level, max_bytes=max_bytes, backup_count=backup_count))
        return _SimpleLogger(logger_name, level, handlers)

    def log_service(self, level: int, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        self.service_logger._log(level, message, extra_fields, exc_info)
    def log_debug(self, level: int, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None:
        self.debug_logger._log(level, message, extra_fields, exc_info)
    def service_info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: self.log_service(logging.INFO, message, extra_fields)
    def service_warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: self.log_service(logging.WARNING, message, extra_fields)
    def service_error(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None: self.log_service(logging.ERROR, message, extra_fields, exc_info)
    def service_critical(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None: self.log_service(logging.CRITICAL, message, extra_fields, exc_info)
    def debug_debug(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: self.log_debug(logging.DEBUG, message, extra_fields)
    def debug_info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: self.log_debug(logging.INFO, message, extra_fields)
    def debug_warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None) -> None: self.log_debug(logging.WARNING, message, extra_fields)
    def debug_error(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: Optional[Exception] = None) -> None: self.log_debug(logging.ERROR, message, extra_fields, exc_info)

# --- 阿里云日志实现 ---
class AliyunLogger(BuiltinLogger):
    """继承自BuiltinLogger，并增加了阿里云日志服务处理程序。"""
    def _create_logger(self, prefix: str, debug: bool = False):
        # 复用父类的创建逻辑
        simple_logger = super()._create_logger(prefix, debug)
        
        # 增加阿里云Handler
        aliyun_config = self._get_aliyun_config()
        if aliyun_config:
            simple_logger.handlers.append(AliyunLogHandler(**aliyun_config))
        return simple_logger

    def _get_aliyun_config(self) -> Optional[Dict[str, Any]]:
        project = os.getenv('ALIYUN_LOG_PROJECT')
        logstore = os.getenv('ALIYUN_LOG_STORE')
        endpoint = os.getenv('ALIYUN_LOG_ENDPOINT')
        access_key_id = os.getenv('ALIYUN_LOG_ACCESS_KEY_ID')
        access_key_secret = os.getenv('ALIYUN_LOG_ACCESS_KEY_SECRET')
        if not all([project, logstore, endpoint, access_key_id, access_key_secret]):
            return None
        return {
            'project': project, 'logstore': logstore, 'endpoint': endpoint,
            'access_key_id': access_key_id, 'access_key_secret': access_key_secret,
            'level': getattr(logging, os.getenv('ALIYUN_LOG_LEVEL', 'INFO').upper())
        }


# --- 日志记录器工厂和缓存 ---
_logger_cache: Dict[str, ILogger] = {}

def get_api_logger(api_name: str) -> ILogger:
    """
    获取API专用的日志记录器实例。
    
    该函数作为日志工厂，根据环境变量 `LOG_TYPE` 创建并缓存不同类型的日志记录器。
    
    Args:
        api_name: API或模块的名称，用于区分日志来源。
        
    Returns:
        一个遵循 `ILogger` 接口的日志记录器实例。
    """
    if api_name in _logger_cache:
        return _logger_cache[api_name]

    log_type = os.getenv('LOG_TYPE', 'logging').lower()
    
    logger: ILogger
    if log_type == 'none':
        logger = NullLogger()
    elif log_type == 'loguru':
        if not LOGURU_AVAILABLE:
            print(f"Warning: LOG_TYPE is 'loguru' but it is not installed. Falling back to 'logging'.", file=sys.stderr)
            logger = BuiltinLogger(api_name)
        else:
            logger = LoguruLogger(api_name)
    elif log_type == 'aliyun':
        if not ALIYUN_LOG_AVAILABLE:
            print(f"Warning: LOG_TYPE is 'aliyun' but 'aliyun-log-python-sdk' is not installed. Falling back to 'logging'.", file=sys.stderr)
            logger = BuiltinLogger(api_name)
        else:
            logger = AliyunLogger(api_name)
    elif log_type == 'logging':
        logger = BuiltinLogger(api_name)
    else:
        print(f"Warning: Unknown LOG_TYPE '{log_type}'. Falling back to 'logging'.", file=sys.stderr)
        logger = BuiltinLogger(api_name)
        
    _logger_cache[api_name] = logger
    print(f"Logger for '{api_name}' created with type '{log_type}'.")
    return logger