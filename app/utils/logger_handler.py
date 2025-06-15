from abc import ABC
import aliyun_log_python_sdk as log


class LoggerHandler(log.Logger, ABC):
    def __init__(self, name):
        super().__init__(name)


class ServiceLoggerHandler(LoggerHandler):
    def __init__(self, name):
        super().__init__(name)



class DebugCallLoggerHandler(LoggerHandler):
    def __init__(self, name):
        super().__init__(name)


