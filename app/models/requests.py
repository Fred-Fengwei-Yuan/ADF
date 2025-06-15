from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class SyncRequest(BaseModel):
    """同步请求数据模型"""
    data: Dict[str, Any] = Field(..., description="要处理的数据")

class AsyncRequest(BaseModel):
    """异步请求数据模型"""
    data: Dict[str, Any] = Field(..., description="要处理的数据")
    callback_url: Optional[str] = Field(None, description="任务完成后的回调URL")

class TaskResponse(BaseModel):
    """任务响应数据模型"""
    task_id: str = Field(..., description="任务ID")
    message: str = Field(..., description="响应消息")

class ErrorResponse(BaseModel):
    """错误响应数据模型"""
    error: str = Field(..., description="错误类型")
    detail: Optional[str] = Field(None, description="错误详情") 