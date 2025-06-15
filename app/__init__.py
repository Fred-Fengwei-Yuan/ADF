"""
算法服务框架 - 核心应用包
~~~~~~~~~~~~~~~~~~~~~~~

这个包提供了算法服务器的核心功能，包括：
- API服务
- 任务队列管理
- 数据处理
- 消息队列集成
- 服务注册
"""

__version__ = "0.1.0"
__author__ = "Fred Yuan"
__email__ = "cjcj188@gmail.com"

from fastapi import FastAPI
from fastmcp import FastMCP
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 初始化FastMCP服务
mcp = FastMCP(os.getenv("MCP_NAME", "algorithm-service"))

# 初始化FastAPI应用
app = FastAPI(
    title="算法服务框架",
    description="提供完整的API服务、并发管理、数据处理、服务注册和日志管理功能",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 挂载MCP服务器
mcp_app = mcp.http_app(path='/mcp')
app.mount("/mcp-server", mcp_app)

# 导入核心组件
from .task_manager import TaskQueueManager
from .data_processer import PreprocessingSystem
from .mq_client import MQClientFactory, MQConfig
from .service_registry import ServiceRegistry

# 初始化组件
task_queue_manager = TaskQueueManager()
preprocessing_system = PreprocessingSystem()
service_registry = ServiceRegistry()

# 初始化消息队列客户端
mq_config = MQConfig()  # 根据实际配置初始化
mq_client = MQClientFactory.create_client("rocketmq", mq_config)

# 导出主要组件
__all__ = [
    'app',
    'mcp',
    'task_queue_manager',
    'preprocessing_system',
    'service_registry',
    'mq_client',
    'TaskQueueManager',
    'PreprocessingSystem',
    'ServiceRegistry',
    'MQClientFactory',
    'MQConfig'
]
