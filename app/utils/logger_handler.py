import logging
import os
from abc import ABC
from typing import Optional, Dict, Any
from aliyun.log import LogClient, LogItem, PutLogsRequest
import time
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LoggerHandler(logging.Logger, ABC):
    """基础日志处理器类"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
        self._log_client: Optional[LogClient] = None
        
    def _get_log_client(self) -> LogClient:
        """获取阿里云日志客户端实例"""
        if self._log_client is None:
            self._log_client = LogClient(
                endpoint=os.getenv('ALIYUN_LOG_ENDPOINT'),
                accessKeyId=os.getenv('ALIYUN_LOG_ACCESS_KEY_ID'),
                accessKeySecret=os.getenv('ALIYUN_LOG_ACCESS_KEY_SECRET')
            )
        return self._log_client


class ServiceLoggerHandler(LoggerHandler):
    """服务日志处理器，用于记录服务级别的日志"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.project = os.getenv('ALIYUN_LOG_PROJECT')
        self.logstore = os.getenv('ALIYUN_LOG_STORE')
        
    def _log(self, level: int, msg: str, args: tuple, exc_info: Optional[Exception] = None,
             extra: Optional[Dict[str, Any]] = None, stack_info: bool = False,
             stacklevel: int = 1) -> None:
        """重写日志记录方法"""
        if self.isEnabledFor(level):
            log_item = LogItem()
            log_item.set_time(int(time.time()))
            log_item.set_contents({
                'level': logging.getLevelName(level),
                'message': msg,
                'logger': self.name,
                'timestamp': datetime.now().isoformat()
            })
            
            if extra:
                log_item.set_contents(extra)
                
            request = PutLogsRequest(self.project, self.logstore, topic='', source='', logitems=[log_item])
            try:
                self._get_log_client().put_logs(request)
            except Exception as e:
                print(f"Failed to send log to Aliyun: {str(e)}")


class DebugCallLoggerHandler(LoggerHandler):
    """调试调用日志处理器，用于记录API调用和调试信息"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.project = os.getenv('ALIYUN_LOG_PROJECT')
        self.logstore = os.getenv('ALIYUN_LOG_STORE')
        
    def _log(self, level: int, msg: str, args: tuple, exc_info: Optional[Exception] = None,
             extra: Optional[Dict[str, Any]] = None, stack_info: bool = False,
             stacklevel: int = 1) -> None:
        """重写日志记录方法"""
        if self.isEnabledFor(level):
            log_item = LogItem()
            log_item.set_time(int(time.time()))
            log_item.set_contents({
                'level': logging.getLevelName(level),
                'message': msg,
                'logger': self.name,
                'timestamp': datetime.now().isoformat(),
                'type': 'debug_call'
            })
            
            if extra:
                log_item.set_contents(extra)
                
            request = PutLogsRequest(self.project, self.logstore, topic='', source='', logitems=[log_item])
            try:
                self._get_log_client().put_logs(request)
            except Exception as e:
                print(f"Failed to send log to Aliyun: {str(e)}")

def CustomRotatingFileHandler(filename: str, maxBytes: int = 10 * 1024 * 1024, backupCount: int = 5):
    """自定义文件轮转处理器"""
    return logging.handlers.RotatingFileHandler(filename, maxBytes, backupCount)

def CustomTimedRotatingFileHandler(filename: str, when: str = 'midnight', interval: int = 1, backupCount: int = 5):
    """自定义时间轮转处理器"""
    return logging.handlers.TimedRotatingFileHandler(filename, when, interval, backupCount)

