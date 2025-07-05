#!/usr/bin/env python3
"""
ADF服务启动脚本
~~~~~~~~~~~~~~

支持从环境变量读取并发配置，灵活启动服务。
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

def main():
    """主函数"""
    # 加载环境变量
    load_dotenv(override=True) 
    
    # 读取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    api_workers = int(os.getenv("API_WORKERS", "4"))
    engine_workers = int(os.getenv("ENGINE_WORKERS", "2"))
    task_queue_size = int(os.getenv("TASK_QUEUE_SIZE", "1000"))
    
    print("🚀 ADF服务启动配置:")
    print(f"   - 服务地址: {host}:{port}")
    print(f"   - API并发数: {api_workers}")
    print(f"   - 引擎并发数: {engine_workers}")
    print(f"   - 任务队列大小: {task_queue_size}")
    print()
    
    # 启动服务
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        workers=api_workers,
        log_level="info"
    )

if __name__ == "__main__":
    main() 