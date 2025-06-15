"""
日志工具模块
~~~~~~~~~~~

提供日志记录功能。
"""

import logging
import os
from typing import Optional

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别，如果为None则使用环境变量中的设置
        
    Returns:
        日志记录器实例
    """
    logger = logging.getLogger(name)
    
    # 设置日志级别
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO')
        level = getattr(logging, level.upper())
    logger.setLevel(level)
    
    # 如果已经有处理器，直接返回
    if logger.handlers:
        return logger
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    
    return logger