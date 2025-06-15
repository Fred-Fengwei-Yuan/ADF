from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class MQConfig:
    """消息队列配置基类"""
    def __init__(self, **kwargs):
        self.config = kwargs

class MQClient(ABC):
    """消息队列客户端抽象基类"""
    
    @abstractmethod
    def connect(self) -> None:
        """建立连接"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        pass
    
    @abstractmethod
    def publish(self, topic: str, message: Dict[str, Any]) -> bool:
        """发布消息"""
        pass
    
    @abstractmethod
    def subscribe(self, topic: str, callback: callable) -> None:
        """订阅消息"""
        pass

class RocketMQConfig(MQConfig):
    """RocketMQ配置类"""
    def __init__(self, name_server: str, group_name: str, **kwargs):
        super().__init__(**kwargs)
        self.name_server = name_server
        self.group_name = group_name

class KafkaConfig(MQConfig):
    """Kafka配置类"""
    def __init__(self, bootstrap_servers: str, group_id: str, **kwargs):
        super().__init__(**kwargs)
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id

class RocketMQClient(MQClient):
    """RocketMQ客户端实现"""
    def __init__(self, config: RocketMQConfig):
        self.config = config
        self.connected = False

class KafkaClient(MQClient):
    """Kafka客户端实现"""
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.connected = False

class MQClientFactory:
    """消息队列客户端工厂类"""
    
    @staticmethod
    def create_client(mq_type: str, config: MQConfig) -> MQClient:
        """
        创建消息队列客户端实例
        
        Args:
            mq_type: 消息队列类型 ('rocketmq' 或 'kafka')
            config: 消息队列配置对象
            
        Returns:
            MQClient: 消息队列客户端实例
        """
        clients = {
            'rocketmq': RocketMQClient,
            'kafka': KafkaClient
        }
        
        if mq_type not in clients:
            raise ValueError(f"不支持的消息队列类型: {mq_type}")
            
        #return clients[mq_type](config)
