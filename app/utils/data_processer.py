"""
数据处理器模块
~~~~~~~~~~~~~

提供数据预处理和后处理功能，包括图像和视频处理。
"""

import os
from typing import Dict, Any, Optional, Union
from PIL import Image
import cv2
import numpy as np
from .logger import get_logger
from ..models.validators import ImageValidationModel, VideoValidationModel

logger = get_logger(__name__)

class PreprocessingSystem:
    """预处理系统"""
    
    def __init__(self):
        """初始化预处理系统"""
        self.supported_image_formats = ['image/jpeg', 'image/png', 'image/gif']
        self.supported_video_formats = ['video/mp4', 'video/avi', 'video/mov']
    
    def preprocess(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理数据
        
        Args:
            data: 要处理的数据
            
        Returns:
            处理后的数据
            
        Raises:
            ValueError: 当数据格式不支持时
        """
        try:
            # 检查数据类型
            if 'image' in data:
                return self._preprocess_image(data)
            elif 'video' in data:
                return self._preprocess_video(data)
            else:
                return data
        except Exception as e:
            logger.error(f"预处理数据时发生错误: {str(e)}")
            raise
    
    def _preprocess_image(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理图像
        
        Args:
            data: 包含图像的数据
            
        Returns:
            处理后的数据
        """
        image_path = data['image']
        
        # 使用Pydantic模型验证图像
        image_validator = ImageValidationModel(
            file_path=image_path,
            max_size_mb=10.0,
            min_width=100,
            min_height=100,
            max_width=4096,
            max_height=4096,
            allowed_formats=self.supported_image_formats
        )
        
        # 处理图像
        with Image.open(image_path) as img:
            # 转换为RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整大小
            if img.size[0] > 1024 or img.size[1] > 1024:
                img.thumbnail((1024, 1024), Image.LANCZOS)
            
            # 保存处理后的图像
            output_path = f"{os.path.splitext(image_path)[0]}_processed.jpg"
            img.save(output_path, 'JPEG', quality=85)
            
            # 更新数据
            data['image'] = output_path
            data['image_info'] = {
                'width': img.size[0],
                'height': img.size[1],
                'format': 'JPEG',
                'mode': 'RGB'
            }
        
        return data
    
    def _preprocess_video(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理视频
        
        Args:
            data: 包含视频的数据
            
        Returns:
            处理后的数据
        """
        video_path = data['video']
        
        # 使用Pydantic模型验证视频
        video_validator = VideoValidationModel(
            file_path=video_path,
            max_duration_seconds=300.0,
            min_width=320,
            min_height=240,
            max_width=3840,
            max_height=2160,
            allowed_formats=self.supported_video_formats
        )
        
        # 处理视频
        cap = cv2.VideoCapture(video_path)
        
        # 获取视频信息
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 如果分辨率太大，进行缩放
        if width > 1920 or height > 1080:
            scale = min(1920 / width, 1080 / height)
            width = int(width * scale)
            height = int(height * scale)
        
        # 创建输出视频
        output_path = f"{os.path.splitext(video_path)[0]}_processed.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # 处理每一帧
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 调整大小
            if frame.shape[1] != width or frame.shape[0] != height:
                frame = cv2.resize(frame, (width, height))
            
            # 写入输出视频
            out.write(frame)
        
        # 释放资源
        cap.release()
        out.release()
        
        # 更新数据
        data['video'] = output_path
        data['video_info'] = {
            'width': width,
            'height': height,
            'fps': fps,
            'frame_count': frame_count,
            'format': 'MP4'
        }
        
        return data

class PostprocessingSystem:
    """后处理系统"""
    
    def __init__(self):
        """初始化后处理系统"""
        pass
    
    def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        后处理结果
        
        Args:
            result: 处理结果
            
        Returns:
            处理后的结果
        """
        # 这里添加后处理逻辑
        return result