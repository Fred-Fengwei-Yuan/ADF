"""
存储客户端模块
~~~~~~~~~~~~~~~

提供统一的存储客户端功能，支持将文件上传到不同的存储服务，如阿里云OSS。
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from .logger import get_api_logger

# 动态导入阿里云OSS SDK
try:
    import oss2
    OSS2_AVAILABLE = True
except ImportError:
    OSS2_AVAILABLE = False

logger = get_api_logger("storage_client")

# --- 存储客户端接口定义 ---
class IStorageClient(ABC):
    """存储客户端接口，定义了所有存储实现必须遵守的方法。"""

    @abstractmethod
    async def upload_file(self, source_path: str, destination_path: str) -> Optional[str]:
        """
        上传文件到存储服务。

        Args:
            source_path: 本地源文件路径。
            destination_path: 在存储服务中的目标路径。

        Returns:
            上传成功后的文件URL，如果失败则返回None。
        """
        pass

# --- 空存储实现 ---
class NullStorageClient(IStorageClient):
    """一个不执行任何操作的空存储客户端，用于禁用上传功能。"""

    async def upload_file(self, source_path: str, destination_path: str) -> Optional[str]:
        logger.debug_info(f"存储功能已禁用 (STORAGE_TYPE=none)，跳过文件 '{source_path}' 的上传。")
        # 在禁用时，可以返回本地路径或None，取决于业务需求
        return f"file://{os.path.abspath(source_path)}"

# --- 阿里云OSS实现 ---
class AliyunOSSClient(IStorageClient):
    """使用aliyun-oss-python-sdk的阿里云OSS客户端。"""

    def __init__(self, endpoint: str, access_key_id: str, access_key_secret: str, bucket_name: str):
        if not OSS2_AVAILABLE:
            raise ImportError("要使用阿里云OSS，请先安装: `uv pip install aliyun-oss-python-sdk`")
        
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
        logger.service_info(f"阿里云OSS客户端初始化完成，Bucket: {self.bucket_name}")

    async def upload_file(self, source_path: str, destination_path: str) -> Optional[str]:
        logger.debug_info(f"开始上传文件 '{source_path}' 到OSS路径 '{destination_path}'...")
        try:
            result = self.bucket.put_object_from_file(destination_path, source_path)
            if result.status == 200:
                # 返回文件的公共访问URL（如果bucket是公共读）
                file_url = f"https://{self.bucket_name}.{self.endpoint}/{destination_path}"
                logger.service_info(f"文件 '{source_path}' 成功上传到OSS，URL: {file_url}")
                return file_url
            else:
                logger.service_error(f"上传文件到OSS失败，状态码: {result.status}")
                return None
        except Exception as e:
            logger.service_error(f"上传文件到OSS时发生异常: {e}", exc_info=e)
            return None

# --- 存储客户端工厂 ---
class StorageClientFactory:
    """存储客户端工厂，根据环境变量创建实例。"""

    @staticmethod
    def create_client() -> IStorageClient:
        """
        根据环境变量创建并返回一个存储客户端实例。
        
        Returns:
            存储客户端实例
        """
        storage_type = os.getenv('STORAGE_TYPE', 'none').lower()

        if storage_type == 'none':
            return NullStorageClient()
        
        elif storage_type == 'oss':
            if not OSS2_AVAILABLE:
                logger.service_warning("环境变量 STORAGE_TYPE=oss，但未安装 'aliyun-oss-python-sdk'，将禁用存储功能。")
                return NullStorageClient()
                
            endpoint = os.getenv('OSS_ENDPOINT')
            access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
            access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
            bucket_name = os.getenv('OSS_BUCKET_NAME')

            if not all([endpoint, access_key_id, access_key_secret, bucket_name]):
                logger.service_error("使用阿里云OSS存储，必须配置所有OSS相关环境变量。将禁用存储功能。")
                return NullStorageClient()
            
            return AliyunOSSClient(endpoint, access_key_id, access_key_secret, bucket_name)
        
        else:
            logger.service_warning(f"不支持的存储类型: '{storage_type}'，将禁用存储功能。")
            return NullStorageClient() 