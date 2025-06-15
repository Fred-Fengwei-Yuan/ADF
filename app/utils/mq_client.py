"""
消息队列客户端模块
~~~~~~~~~~~~~~~

提供消息队列客户端功能，支持多种消息队列系统。
"""

import os
import json
from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from .logger import get_logger

logger = get_logger(__name__)

class MQConfig:
    """消息队列配置"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 9876,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs
    ):
        """
        初始化消息队列配置
        
        Args:
            host: 服务器地址
            port: 服务器端口
            username: 用户名
            password: 密码
            **kwargs: 其他配置参数
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.extra_config = kwargs

class MQClient(ABC):
    """消息队列客户端基类"""
    
    @abstractmethod
    async def connect(self) -> None:
        """连接到消息队列服务器"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """断开与消息队列服务器的连接"""
        pass
    
    @abstractmethod
    async def send_message(self, topic: str, message: Dict[str, Any]) -> None:
        """
        发送消息
        
        Args:
            topic: 主题
            message: 消息内容
        """
        pass
    
    @abstractmethod
    async def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        订阅主题
        
        Args:
            topic: 主题
            callback: 回调函数
        """
        pass

class RocketMQClient(MQClient):
    """RocketMQ客户端"""
    
    def __init__(self, config: MQConfig):
        """
        初始化RocketMQ客户端
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.producer = None
        self.consumer = None
    
    async def connect(self) -> None:
        """连接到RocketMQ服务器"""
        try:
            # 这里添加实际的RocketMQ连接逻辑
            logger.info(f"连接到RocketMQ服务器 {self.config.host}:{self.config.port}")
        except Exception as e:
            logger.error(f"连接RocketMQ服务器失败: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """断开与RocketMQ服务器的连接"""
        try:
            # 这里添加实际的断开连接逻辑
            logger.info("断开与RocketMQ服务器的连接")
        except Exception as e:
            logger.error(f"断开RocketMQ连接失败: {str(e)}")
            raise
    
    async def send_message(self, topic: str, message: Dict[str, Any]) -> None:
        """
        发送消息到RocketMQ
        
        Args:
            topic: 主题
            message: 消息内容
        """
        try:
            # 这里添加实际的发送消息逻辑
            message_str = json.dumps(message)
            logger.info(f"发送消息到主题 {topic}: {message_str}")
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
            raise
    
    async def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        订阅RocketMQ主题
        
        Args:
            topic: 主题
            callback: 回调函数
        """
        try:
            # 这里添加实际的订阅逻辑
            logger.info(f"订阅主题 {topic}")
        except Exception as e:
            logger.error(f"订阅主题失败: {str(e)}")
            raise

class KafkaClient(MQClient):
    """Kafka客户端"""
    
    def __init__(self, config: MQConfig):
        """
        初始化Kafka客户端
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.producer = None
        self.consumer = None
    
    async def connect(self) -> None:
        """连接到Kafka服务器"""
        try:
            # 这里添加实际的Kafka连接逻辑
            logger.info(f"连接到Kafka服务器 {self.config.host}:{self.config.port}")
        except Exception as e:
            logger.error(f"连接Kafka服务器失败: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """断开与Kafka服务器的连接"""
        try:
            # 这里添加实际的断开连接逻辑
            logger.info("断开与Kafka服务器的连接")
        except Exception as e:
            logger.error(f"断开Kafka连接失败: {str(e)}")
            raise
    
    async def send_message(self, topic: str, message: Dict[str, Any]) -> None:
        """
        发送消息到Kafka
        
        Args:
            topic: 主题
            message: 消息内容
        """
        try:
            # 这里添加实际的发送消息逻辑
            message_str = json.dumps(message)
            logger.info(f"发送消息到主题 {topic}: {message_str}")
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
            raise
    
    async def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        订阅Kafka主题
        
        Args:
            topic: 主题
            callback: 回调函数
        """
        try:
            # 这里添加实际的订阅逻辑
            logger.info(f"订阅主题 {topic}")
        except Exception as e:
            logger.error(f"订阅主题失败: {str(e)}")
            raise

class MQClientFactory:
    """消息队列客户端工厂"""
    
    @staticmethod
    def create_client(mq_type: str, config: MQConfig) -> MQClient:
        """
        创建消息队列客户端
        
        Args:
            mq_type: 消息队列类型（'rocketmq' 或 'kafka'）
            config: 配置对象
            
        Returns:
            消息队列客户端实例
            
        Raises:
            ValueError: 当消息队列类型不支持时
        """
        if mq_type.lower() == 'rocketmq':
            return RocketMQClient(config)
        elif mq_type.lower() == 'kafka':
            return KafkaClient(config)
        else:
            raise ValueError(f"不支持的消息队列类型: {mq_type}")
