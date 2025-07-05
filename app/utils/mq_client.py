"""
消息队列客户端模块
~~~~~~~~~~~~~~~

提供消息队列客户端功能，支持多种消息队列系统。
"""

import os
import json
from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from .logger import get_api_logger

# 动态导入pika
try:
    import pika
    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False

logger = get_api_logger("mq_client")

class MQConfig:
    """消息队列配置"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 9876,
        username: str | None = None,
        password: str | None = None,
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

# --- 新增：空消息队列客户端 ---
class NullMQClient(MQClient):
    """一个不执行任何操作的空消息队列客户端，用于禁用消息队列功能。"""
    async def connect(self) -> None:
        logger.debug_info("消息队列功能已禁用 (MQ_TYPE=none)，跳过连接。")
        pass
    
    async def disconnect(self) -> None:
        pass
    
    async def send_message(self, topic: str, message: Dict[str, Any]) -> None:
        logger.debug_info(f"消息队列功能已禁用，模拟发送消息到主题 {topic}。")
        pass
    
    async def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        logger.debug_info(f"消息队列功能已禁用，无法订阅主题 {topic}。")
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
            logger.service_info(f"连接到RocketMQ服务器 {self.config.host}:{self.config.port}")
        except Exception as e:
            logger.service_error(f"连接RocketMQ服务器失败: {str(e)}", exc_info=e)
            raise
    
    async def disconnect(self) -> None:
        """断开与RocketMQ服务器的连接"""
        try:
            # 这里添加实际的断开连接逻辑
            logger.service_info("断开与RocketMQ服务器的连接")
        except Exception as e:
            logger.service_error(f"断开RocketMQ连接失败: {str(e)}", exc_info=e)
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
            logger.service_info(f"发送消息到主题 {topic}: {message_str}")
        except Exception as e:
            logger.service_error(f"发送消息失败: {str(e)}", exc_info=e)
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
            logger.service_info(f"订阅主题 {topic}")
        except Exception as e:
            logger.service_error(f"订阅主题失败: {str(e)}", exc_info=e)
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
            logger.service_info(f"连接到Kafka服务器 {self.config.host}:{self.config.port}")
        except Exception as e:
            logger.service_error(f"连接Kafka服务器失败: {str(e)}", exc_info=e)
            raise
    
    async def disconnect(self) -> None:
        """断开与Kafka服务器的连接"""
        try:
            # 这里添加实际的断开连接逻辑
            logger.service_info("断开与Kafka服务器的连接")
        except Exception as e:
            logger.service_error(f"断开Kafka连接失败: {str(e)}", exc_info=e)
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
            logger.service_info(f"发送消息到主题 {topic}: {message_str}")
        except Exception as e:
            logger.service_error(f"发送消息失败: {str(e)}", exc_info=e)
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
            logger.service_info(f"订阅主题 {topic}")
        except Exception as e:
            logger.service_error(f"订阅主题失败: {str(e)}", exc_info=e)
            raise

# --- 新增：RabbitMQ客户端 ---
class RabbitMQClient(MQClient):
    """RabbitMQ客户端 (使用pika库)"""
    def __init__(self, config: MQConfig):
        self.config = config
        self.connection = None
        self.channel = None

    async def connect(self) -> None:
        if not PIKA_AVAILABLE:
            raise ImportError("RabbitMQ需要pika库，请运行 'pip install pika'")
        try:
            credentials = pika.PlainCredentials(self.config.username, self.config.password)
            parameters = pika.ConnectionParameters(
                host=self.config.host,
                port=self.config.port,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.service_info(f"连接到RabbitMQ服务器 {self.config.host}:{self.config.port}")
        except Exception as e:
            logger.service_error(f"连接RabbitMQ服务器失败: {str(e)}", exc_info=e)
            raise

    async def disconnect(self) -> None:
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
                logger.service_info("断开与RabbitMQ服务器的连接")
        except Exception as e:
            logger.service_error(f"断开RabbitMQ连接失败: {str(e)}", exc_info=e)
            raise

    async def send_message(self, topic: str, message: Dict[str, Any]) -> None:
        if not self.channel:
            await self.connect()
        
        try:
            self.channel.queue_declare(queue=topic, durable=True)
            message_str = json.dumps(message)
            self.channel.basic_publish(
                exchange='',
                routing_key=topic,
                body=message_str,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))
            logger.service_info(f"发送消息到RabbitMQ主题 {topic}: {message_str}")
        except Exception as e:
            logger.service_error(f"发送RabbitMQ消息失败: {str(e)}", exc_info=e)
            raise

    async def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        # 注意: pika是同步库，在异步环境中使用需要额外处理，例如在独立线程中运行。
        # 此处提供一个简化的同步实现作为示例。
        if not self.channel:
            await self.connect()

        self.channel.queue_declare(queue=topic, durable=True)
        logger.service_info(f"开始从RabbitMQ订阅主题 {topic}")

        def pika_callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.service_error(f"处理RabbitMQ消息失败: {e}", exc_info=e)

        self.channel.basic_consume(queue=topic, on_message_callback=pika_callback)
        
        # 因为pika是阻塞的，需要在另一个线程中启动消费
        logger.service_info(f"订阅了主题 {topic}，等待消息。请注意在生产环境中应在独立线程中运行 `start_consuming`。")
        # self.channel.start_consuming() 

class MQClientFactory:
    """消息队列客户端工厂"""
    
    @staticmethod
    def create_client() -> MQClient:
        """
        根据环境变量创建并返回一个消息队列客户端实例。
        
        Returns:
            消息队列客户端实例
        """
        mq_type = os.getenv('MQ_TYPE', 'none').lower()

        if mq_type == 'none':
            return NullMQClient()

        config = MQConfig(
            host=os.getenv('MQ_HOST', 'localhost'),
            port=int(os.getenv('MQ_PORT', 0)), # 让具体实现处理默认端口
            username=os.getenv('MQ_USERNAME'),
            password=os.getenv('MQ_PASSWORD')
        )

        if mq_type == "rocketmq":
            if not config.port: config.port = 9876
            return RocketMQClient(config)
        elif mq_type == "kafka":
            if not config.port: config.port = 9092
            return KafkaClient(config)
        elif mq_type == "rabbitmq":
            if not PIKA_AVAILABLE:
                raise ImportError("要使用RabbitMQ，请先安装pika: `uv pip install pika`")
            if not config.port: config.port = 5672
            return RabbitMQClient(config)
        else:
            logger.service_warning(f"不支持的消息队列类型: {mq_type}，将禁用消息队列功能。")
            return NullMQClient()
