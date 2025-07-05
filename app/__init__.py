"""
算法服务框架 - 核心应用包
~~~~~~~~~~~~~~~~~~~~~~~

本包提供算法服务的核心功能，包括：
- API服务
- 任务队列管理
- 数据处理
- 消息队列集成
- 服务注册
"""

__version__ = "0.1.0"
__author__ = "Fred Yuan"
__email__ = "cjcj188@gmail.com"

# 导入核心组件
from .utils import (
    TaskQueueManager,
    PreprocessingSystem,
    MQClientFactory,
    MQConfig,
    ServiceRegistry,
    StorageClientFactory,
    IStorageClient
)

__all__ = [
    'TaskQueueManager',
    'PreprocessingSystem',
    'ServiceRegistry',
    'MQClientFactory',
    'MQConfig',
    'StorageClientFactory',
    'IStorageClient'
]
