"""
任务管理器模块
~~~~~~~~~~~~~

提供任务队列管理和任务状态跟踪功能。
"""

import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from .logger import get_logger

logger = get_logger(__name__)

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
    
    def __init__(self, max_workers: int = 10):
        """
        初始化任务队列管理器
        
        Args:
            max_workers: 最大工作线程数
        """
        self.tasks: Dict[str, Task] = {}
        self.queue = asyncio.Queue()
        self.max_workers = max_workers
        self.workers = []
        self._started = False
    
    async def start(self):
        """启动任务队列管理器"""
        if not self._started:
            self._start_workers()
            self._started = True
            logger.info("任务队列管理器已启动")
    
    def _start_workers(self):
        """启动工作线程"""
        for _ in range(self.max_workers):
            worker = asyncio.create_task(self._worker())
            self.workers.append(worker)
    
    async def _worker(self):
        """工作线程函数"""
        while True:
            try:
                task = await self.queue.get()
                await self._process_task(task)
                self.queue.task_done()
            except Exception as e:
                logger.error(f"处理任务时发生错误: {str(e)}")
    
    async def _process_task(self, task: Task):
        """
        处理任务
        
        Args:
            task: 要处理的任务
        """
        try:
            # 更新任务状态为处理中
            task.update_status("processing")
            
            # 这里添加实际的任务处理逻辑
            # 示例：模拟处理过程
            await asyncio.sleep(1)
            result = {"processed": task.data}
            
            # 更新任务状态为完成
            task.update_status("completed", result=result)
            
        except Exception as e:
            # 更新任务状态为失败
            task.update_status("failed", error=str(e))
            logger.error(f"任务 {task.id} 处理失败: {str(e)}")
    
    def add_task(self, data: Dict[str, Any]) -> str:
        """
        添加任务到队列
        
        Args:
            data: 任务数据
            
        Returns:
            任务ID
        """
        task = Task(data)
        self.tasks[task.id] = task
        self.queue.put_nowait(task)
        logger.info(f"添加任务 {task.id} 到队列")
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
    
    async def stop(self):
        """停止任务队列管理器"""
        # 等待所有任务完成
        await self.queue.join()
        
        # 取消所有工作线程
        for worker in self.workers:
            worker.cancel()
        
        # 等待所有工作线程结束
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        logger.info("任务队列管理器已停止") 