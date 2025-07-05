"""
主应用入口模块
~~~~~~~~~~~~~

这个模块定义了API路由和请求处理逻辑, 同时支持RESTful API和MCP工具调用.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.routing import Mount
from typing import Dict, Any, Optional, List
import os
import time
import uuid
from fastmcp import FastMCP

from .utils import TaskQueueManager, PreprocessingSystem, MQClientFactory, MQConfig, ServiceRegistry, get_api_logger, StorageClientFactory, IStorageClient
from .models.requests import SyncRequest, AsyncRequest, TaskResponse, ErrorResponse

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
mq_client = MQClientFactory.create_client()

# 初始化存储客户端
storage_client = StorageClientFactory.create_client()

# 初始化API日志记录器
sync_api_logger = get_api_logger("sync_api")
async_api_logger = get_api_logger("async_api")
task_status_api_logger = get_api_logger("task_status_api")
queue_stats_api_logger = get_api_logger("queue_stats_api")

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
    request_id = str(uuid.uuid4())
    
    # 记录服务日志 - API输入
    sync_api_logger.service_info("同步处理API调用开始", extra_fields={
        "request_id": request_id,
        "input_data": str(data)[:500]  # 限制长度避免日志过大
    })
    
    # 记录调试日志 - 服务状态
    sync_api_logger.debug_info("开始数据预处理", extra_fields={
        "request_id": request_id,
        "data_type": type(data).__name__,
        "data_keys": list(data.keys()) if isinstance(data, dict) else None
    })
    
    try:
        # 记录调试日志 - 引擎状态
        sync_api_logger.debug_info("预处理系统状态检查", extra_fields={
            "request_id": request_id,
            "preprocessing_system_ready": True
        })
        
        processed_data = preprocessing_system.preprocess(data)
        
        # 记录调试日志 - 中间过程
        sync_api_logger.debug_info("数据预处理完成", extra_fields={
            "request_id": request_id,
            "processed_data_keys": list(processed_data.keys()) if isinstance(processed_data, dict) else None
        })
        
        result = processed_data  # 这里替换为实际的算法处理逻辑
        
        # 记录调试日志 - 处理结果
        sync_api_logger.debug_info("算法处理完成", extra_fields={
            "request_id": request_id,
            "result_type": type(result).__name__,
            "result_keys": list(result.keys()) if isinstance(result, dict) else None
        })
        
        # 记录服务日志 - API输出
        sync_api_logger.service_info("同步处理API调用成功", extra_fields={
            "request_id": request_id,
            "output_data": str(result)[:500]  # 限制长度避免日志过大
        })
        
        return result
        
    except Exception as e:
        # 记录服务日志 - API错误
        sync_api_logger.service_error("同步处理API调用失败", extra_fields={
            "request_id": request_id,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }, exc_info=e)
        
        # 记录调试日志 - 错误详情
        sync_api_logger.debug_error("处理过程中发生异常", extra_fields={
            "request_id": request_id,
            "exception_details": str(e)
        }, exc_info=e)
        
        raise Exception(f"处理请求时发生错误: {str(e)}")

@mcp.tool("process_async")
async def process_async_tool(
    data: Dict[str, Any],
    callback_url: str | None
) -> TaskResponse:
    """
    异步处理工具
    
    Args:
        data: 要处理的数据
        callback_url: 任务完成后的回调URL
        
    Returns:
        任务响应
    """
    request_id = str(uuid.uuid4())
    
    # 记录服务日志 - API输入
    async_api_logger.service_info("异步处理API调用开始", extra_fields={
        "request_id": request_id,
        "input_data": str(data)[:500],
        "callback_url": callback_url
    })
    
    # 记录调试日志 - 服务状态
    async_api_logger.debug_info("开始异步任务处理", extra_fields={
        "request_id": request_id,
        "data_type": type(data).__name__,
        "has_callback": callback_url is not None
    })
    
    try:
        # 记录调试日志 - 引擎状态
        async_api_logger.debug_info("任务队列管理器状态检查", extra_fields={
            "request_id": request_id,
            "queue_manager_ready": True,
            "max_workers": task_queue_manager.max_workers
        })
        
        processed_data = preprocessing_system.preprocess(data)
        
        # 记录调试日志 - 中间过程
        async_api_logger.debug_info("数据预处理完成，准备提交任务", extra_fields={
            "request_id": request_id,
            "processed_data_keys": list(processed_data.keys()) if isinstance(processed_data, dict) else None
        })
        
        task_id = task_queue_manager.add_task(processed_data)
        
        # 记录调试日志 - 任务创建
        async_api_logger.debug_info("任务已创建并加入队列", extra_fields={
            "request_id": request_id,
            "task_id": task_id,
            "queue_size": task_queue_manager.queue.qsize()
        })
        
        if callback_url:
            # 记录调试日志 - 消息队列操作
            async_api_logger.debug_info("发送任务状态消息到消息队列", extra_fields={
                "request_id": request_id,
                "task_id": task_id,
                "topic": "task_status",
                "callback_url": callback_url
            })
            
            await mq_client.send_message(
                topic="task_status",
                message={
                    "task_id": task_id,
                    "status": "submitted",
                    "callback_url": callback_url
                }
            )
        
        response = TaskResponse(
            task_id=task_id,
            message="任务已成功提交"
        )
        
        # 记录服务日志 - API输出
        async_api_logger.service_info("异步处理API调用成功", extra_fields={
            "request_id": request_id,
            "task_id": task_id,
            "response_message": response.message
        })
        
        return response
        
    except Exception as e:
        # 记录服务日志 - API错误
        async_api_logger.service_error("异步处理API调用失败", extra_fields={
            "request_id": request_id,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }, exc_info=e)
        
        # 记录调试日志 - 错误详情
        async_api_logger.debug_error("异步处理过程中发生异常", extra_fields={
            "request_id": request_id,
            "exception_details": str(e)
        }, exc_info=e)
        
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
    request_id = str(uuid.uuid4())
    
    # 记录服务日志 - API输入
    task_status_api_logger.service_info("获取任务状态API调用开始", extra_fields={
        "request_id": request_id,
        "task_id": task_id
    })
    
    # 记录调试日志 - 服务状态
    task_status_api_logger.debug_info("开始查询任务状态", extra_fields={
        "request_id": request_id,
        "task_id": task_id,
        "queue_manager_ready": True
    })
    
    try:
        status = task_queue_manager.get_task_status(task_id)
        
        if status is None:
            # 记录服务日志 - API错误
            task_status_api_logger.service_error("任务不存在", extra_fields={
                "request_id": request_id,
                "task_id": task_id,
                "error_type": "TaskNotFound"
            })
            
            raise Exception(f"任务 {task_id} 不存在")
        
        # 记录调试日志 - 查询结果
        task_status_api_logger.debug_info("任务状态查询成功", extra_fields={
            "request_id": request_id,
            "task_id": task_id,
            "task_status": status.get("status"),
            "task_created_at": status.get("created_at")
        })
        
        # 记录服务日志 - API输出
        task_status_api_logger.service_info("获取任务状态API调用成功", extra_fields={
            "request_id": request_id,
            "task_id": task_id,
            "task_status": status.get("status"),
            "output_data": str(status)[:500]
        })
        
        return status
        
    except Exception as e:
        # 记录服务日志 - API错误
        task_status_api_logger.service_error("获取任务状态API调用失败", extra_fields={
            "request_id": request_id,
            "task_id": task_id,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }, exc_info=e)
        
        # 记录调试日志 - 错误详情
        task_status_api_logger.debug_error("查询任务状态时发生异常", extra_fields={
            "request_id": request_id,
            "task_id": task_id,
            "exception_details": str(e)
        }, exc_info=e)
        
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

@app.get('/api/v1/queue/stats', response_model=Dict[str, Any])
async def get_queue_stats():
    """
    获取队列统计信息接口
    
    Returns:
        队列统计信息
        
    Raises:
        HTTPException: 当查询过程中发生错误时
    """
    request_id = str(uuid.uuid4())
    
    # 记录服务日志 - API输入
    queue_stats_api_logger.service_info("获取队列统计信息API调用开始", extra_fields={
        "request_id": request_id
    })
    
    try:
        stats = task_queue_manager.get_queue_stats()
        
        # 记录服务日志 - API输出
        queue_stats_api_logger.service_info("获取队列统计信息API调用成功", extra_fields={
            "request_id": request_id,
            "queue_size": stats.get("queue_size"),
            "active_workers": stats.get("active_workers"),
            "total_tasks": stats.get("total_tasks")
        })
        
        return stats
        
    except Exception as e:
        # 记录服务日志 - API错误
        queue_stats_api_logger.service_error("获取队列统计信息API调用失败", extra_fields={
            "request_id": request_id,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }, exc_info=e)
        
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
    # 记录全局异常
    global_logger = get_api_logger("global")
    global_logger.service_error("全局异常处理器捕获到异常", extra_fields={
        "request_path": str(request.url),
        "request_method": request.method,
        "error_type": type(exc).__name__,
        "error_message": str(exc)
    }, exc_info=exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc)
        }
    )