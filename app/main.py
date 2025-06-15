"""
主应用入口模块
~~~~~~~~~~~~~

这个模块定义了API路由和请求处理逻辑，同时支持RESTful API和MCP工具调用。
"""

from fastmcp import FastMCP
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.routing import Mount
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from dotenv import load_dotenv
import os

from .task_manager import TaskQueueManager
from .data_processer import PreprocessingSystem
from .mq_client import MQClientFactory, MQConfig
from .service_registry import ServiceRegistry

# 加载环境变量
load_dotenv()

# 初始化FastMCP服务
mcp = FastMCP(os.getenv("MCP_NAME"))

# 初始化ASGI应用
mcp_app = mcp.http_app(path='/mcp')

# 初始化FastAPI应用并挂载MCP服务器
app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/mcp-server", mcp_app)

# 初始化组件
task_queue_manager = TaskQueueManager()
preprocessing_system = PreprocessingSystem()
service_registry = ServiceRegistry()

# 初始化消息队列客户端
mq_config = MQConfig()  # 根据实际配置初始化
mq_client = MQClientFactory.create_client("rocketmq", mq_config)

# 请求模型定义
class SyncRequest(BaseModel):
    """同步请求数据模型"""
    data: Dict[str, Any] = Field(..., description="要处理的数据")

class AsyncRequest(BaseModel):
    """异步请求数据模型"""
    data: Dict[str, Any] = Field(..., description="要处理的数据")
    callback_url: Optional[str] = Field(None, description="任务完成后的回调URL")

# 响应模型定义
class TaskResponse(BaseModel):
    """任务响应数据模型"""
    task_id: str = Field(..., description="任务ID")
    message: str = Field(..., description="响应消息")

class ErrorResponse(BaseModel):
    """错误响应数据模型"""
    error: str = Field(..., description="错误类型")
    detail: Optional[str] = Field(None, description="错误详情")

# MCP工具定义
@mcp.tool("process_sync")
async def process_sync_tool(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    同步处理工具
    
    Args:
        data: 要处理的数据
        
    Returns:
        处理结果
    """
    try:
        processed_data = preprocessing_system.preprocess(data)
        result = processed_data  # 这里替换为实际的算法处理逻辑
        return result
    except Exception as e:
        raise Exception(f"处理请求时发生错误: {str(e)}")

@mcp.tool("process_async")
async def process_async_tool(
    data: Dict[str, Any],
    callback_url: Optional[str] = None
) -> TaskResponse:
    """
    异步处理工具
    
    Args:
        data: 要处理的数据
        callback_url: 任务完成后的回调URL
        
    Returns:
        任务响应
    """
    try:
        processed_data = preprocessing_system.preprocess(data)
        task_id = task_queue_manager.add_task(processed_data)
        
        if callback_url:
            await mq_client.send_message(
                topic="task_status",
                message={
                    "task_id": task_id,
                    "status": "submitted",
                    "callback_url": callback_url
                }
            )
        
        return TaskResponse(
            task_id=task_id,
            message="任务已成功提交"
        )
    except Exception as e:
        raise Exception(f"提交任务时发生错误: {str(e)}")

@mcp.tool("get_task_status")
async def get_task_status_tool(task_id: str) -> Dict[str, Any]:
    """
    获取任务状态工具
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态信息
    """
    try:
        status = task_queue_manager.get_task_status(task_id)
        if status is None:
            raise Exception(f"任务 {task_id} 不存在")
        return status
    except Exception as e:
        raise Exception(f"查询任务状态时发生错误: {str(e)}")

# RESTful API路由
@app.post('/api/v1/sync', response_model=Dict[str, Any])
async def sync_api(request: SyncRequest):
    """
    同步处理接口
    
    Args:
        request: 包含处理数据的请求对象
        
    Returns:
        处理结果
        
    Raises:
        HTTPException: 当处理过程中发生错误时
    """
    try:
        return await process_sync_tool(request.data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post('/api/v1/async', response_model=TaskResponse)
async def async_api(request: AsyncRequest):
    """
    异步处理接口
    
    Args:
        request: 包含处理数据和回调URL的请求对象
        
    Returns:
        包含任务ID的响应对象
        
    Raises:
        HTTPException: 当任务提交过程中发生错误时
    """
    try:
        return await process_async_tool(request.data, request.callback_url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get('/api/v1/task/{task_id}', response_model=Dict[str, Any])
async def get_task_status(task_id: str):
    """
    获取任务状态接口
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态信息
        
    Raises:
        HTTPException: 当任务不存在或查询过程中发生错误时
    """
    try:
        return await get_task_status_tool(task_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    
    Args:
        request: 请求对象
        exc: 异常对象
        
    Returns:
        错误响应
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc)
        }
    )