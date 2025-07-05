"""
任务管理器模块
~~~~~~~~~~~~~

提供任务队列管理和任务状态跟踪功能。
"""

import asyncio
import uuid
import os
from typing import Dict, Any, Optional
from datetime import datetime
from .logger import get_api_logger

logger = get_api_logger("task_manager")

class Task:
    """任务类"""
    
    def __init__(self, data: Dict[str, Any]):
        """
        初始化任务
        
        Args:
            data: 任务数据
        """
        self.id = str(uuid.uuid4())
        self.data = data
        self.status = "pending"
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.updated_at = self.created_at
    
    def update_status(self, status: str, result: Optional[Any] = None, error: Optional[str] = None):
        """
        更新任务状态
        
        Args:
            status: 新状态
            result: 处理结果
            error: 错误信息
        """
        self.status = status
        self.result = result
        self.error = error
        self.updated_at = datetime.now()

class TaskQueueManager:
    """任务队列管理器"""
    
    def __init__(self, max_workers: Optional[int] = None, queue_size: Optional[int] = None):
        """
        初始化任务队列管理器
        
        Args:
            max_workers: 最大工作线程数（引擎并发数）
            queue_size: 任务队列最大大小
        """
        # 从环境变量读取配置，支持动态配置
        self.max_workers = max_workers or int(os.getenv("ENGINE_WORKERS", "2"))
        self.queue_size = queue_size or int(os.getenv("TASK_QUEUE_SIZE", "1000"))
        
        self.tasks: Dict[str, Task] = {}
        self.queue = asyncio.Queue(maxsize=self.queue_size)
        self.workers = []
        self._started = False
        self._stop_event = asyncio.Event()
        
        logger.service_info(f"任务队列管理器初始化完成", extra_fields={
            "max_workers": self.max_workers,
            "queue_size": self.queue_size
        })
    
    async def start(self):
        """启动任务队列管理器"""
        if not self._started:
            self._start_workers()
            self._started = True
            logger.service_info("任务队列管理器已启动", extra_fields={
                "active_workers": len(self.workers),
                "max_workers": self.max_workers
            })
    
    def _start_workers(self):
        """启动工作线程"""
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i+1}"))
            self.workers.append(worker)
            logger.debug_info(f"启动工作线程 {i+1}/{self.max_workers}")
    
    async def _worker(self, worker_name: str):
        """工作线程函数"""
        logger.debug_info(f"工作线程 {worker_name} 开始运行")
        
        while not self._stop_event.is_set():
            try:
                # 等待任务，支持超时以便检查停止信号
                try:
                    task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                logger.debug_info(f"工作线程 {worker_name} 开始处理任务", extra_fields={
                    "task_id": task.id,
                    "queue_size": self.queue.qsize()
                })
                
                await self._process_task(task, worker_name)
                self.queue.task_done()
                
            except asyncio.CancelledError:
                logger.debug_info(f"工作线程 {worker_name} 被取消")
                break
            except Exception as e:
                logger.service_error(f"工作线程 {worker_name} 处理任务时发生错误: {str(e)}", exc_info=e)
        
        logger.debug_info(f"工作线程 {worker_name} 已停止")
    
    async def _process_task(self, task: Task, worker_name: str):
        """
        处理任务
        
        Args:
            task: 要处理的任务
            worker_name: 工作线程名称
        """
        try:
            # 更新任务状态为处理中
            task.update_status("processing")
            
            logger.debug_info(f"开始处理任务", extra_fields={
                "task_id": task.id,
                "worker_name": worker_name,
                "data_type": type(task.data).__name__
            })
            
            # 这里添加实际的任务处理逻辑
            # 示例：模拟处理过程
            await asyncio.sleep(1)
            result = {"processed": task.data, "worker": worker_name}
            
            # 更新任务状态为完成
            task.update_status("completed", result=result)
            
            logger.debug_info(f"任务处理完成", extra_fields={
                "task_id": task.id,
                "worker_name": worker_name,
                "status": "completed"
            })
            
        except Exception as e:
            # 更新任务状态为失败
            task.update_status("failed", error=str(e))
            logger.service_error(f"任务 {task.id} 处理失败", extra_fields={
                "worker_name": worker_name,
                "error": str(e)
            }, exc_info=e)
    
    def add_task(self, data: Dict[str, Any]) -> str:
        """
        添加任务到队列
        
        Args:
            data: 任务数据
            
        Returns:
            任务ID
        """
        # 检查队列是否已满
        if self.queue.full():
            logger.service_error("任务队列已满，无法添加新任务", extra_fields={
                "queue_size": self.queue.qsize(),
                "max_size": self.queue_size
            })
            raise Exception("任务队列已满，请稍后重试")
        
        task = Task(data)
        self.tasks[task.id] = task
        
        try:
            self.queue.put_nowait(task)
            logger.service_info(f"添加任务到队列", extra_fields={
                "task_id": task.id,
                "queue_size": self.queue.qsize(),
                "max_size": self.queue_size
            })
        except asyncio.QueueFull:
            logger.service_error("任务队列已满", extra_fields={
                "task_id": task.id,
                "queue_size": self.queue.qsize()
            })
            raise Exception("任务队列已满")
        
        return task.id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息，如果任务不存在则返回None
        """
        task = self.tasks.get(task_id)
        if task is None:
            return None
        
        return {
            "id": task.id,
            "status": task.status,
            "result": task.result,
            "error": task.error,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        获取队列统计信息
        
        Returns:
            队列统计信息
        """
        return {
            "queue_size": self.queue.qsize(),
            "max_queue_size": self.queue_size,
            "active_workers": len(self.workers),
            "max_workers": self.max_workers,
            "total_tasks": len(self.tasks),
            "is_started": self._started
        }
    
    async def stop(self):
        """停止任务队列管理器"""
        logger.service_info("开始停止任务队列管理器")
        
        # 设置停止信号
        self._stop_event.set()
        
        # 等待所有任务完成
        await self.queue.join()
        
        # 取消所有工作线程
        for worker in self.workers:
            worker.cancel()
        
        # 等待所有工作线程结束
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        logger.service_info("任务队列管理器已停止") 