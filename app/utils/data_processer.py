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
from .logger import get_api_logger
from ..models.validators import ImageValidationModel, VideoValidationModel

logger = get_api_logger("data_processer")

class PreprocessingSystem:
    """预处理系统"""
    
    def __init__(self):
        """
        初始化预处理系统，并从环境变量加载配置。
        """
        self.supported_image_formats = ['image/jpeg', 'image/png', 'image/gif']
        self.supported_video_formats = ['video/mp4', 'video/avi', 'video/mov']

        # 从环境变量加载配置，并提供合理的默认值
        self.max_image_width = int(os.getenv('PREPROCESS_MAX_IMAGE_WIDTH', 4096))
        self.max_image_height = int(os.getenv('PREPROCESS_MAX_IMAGE_HEIGHT', 4096))
        self.max_video_seconds = float(os.getenv('PREPROCESS_MAX_VIDEO_SECONDS', 300.0))
        
        # 其他可配置参数
        self.image_output_quality = int(os.getenv('PREPROCESS_IMAGE_QUALITY', 85))
        self.video_output_width = int(os.getenv('PREPROCESS_VIDEO_WIDTH', 1920))
        self.video_output_height = int(os.getenv('PREPROCESS_VIDEO_HEIGHT', 1080))

        logger.service_info("预处理系统初始化完成", extra_fields={
            "max_image_width": self.max_image_width,
            "max_image_height": self.max_image_height,
            "max_video_seconds": self.max_video_seconds
        })

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
            logger.service_error(f"预处理数据时发生错误: {str(e)}", exc_info=e)
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
            max_width=self.max_image_width,
            max_height=self.max_image_height,
            allowed_formats=self.supported_image_formats
        )
        
        # 处理图像
        with Image.open(image_path) as img:
            # 转换为RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整大小 (使用配置)
            if img.size[0] > self.max_image_width or img.size[1] > self.max_image_height:
                img.thumbnail((self.max_image_width, self.max_image_height), Image.LANCZOS)
            
            # 保存处理后的图像
            output_path = f"{os.path.splitext(image_path)[0]}_processed.jpg"
            img.save(output_path, 'JPEG', quality=self.image_output_quality)
            
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
            max_duration_seconds=self.max_video_seconds,
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
        
        # 如果分辨率太大，进行缩放 (使用配置)
        if width > self.video_output_width or height > self.video_output_height:
            scale = min(self.video_output_width / width, self.video_output_height / height)
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