"""
数据验证模型模块
~~~~~~~~~~~~~~~

使用Pydantic定义所有数据验证模型，包括图像、视频和文本验证。
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
import os
from PIL import Image
import cv2
import magic
import langdetect

class BaseValidationModel(BaseModel):
    """基础验证模型"""
    pass

class TextValidationModel(BaseValidationModel):
    """文本验证模型"""
    text: str = Field(..., description="要验证的文本")
    min_length: int = Field(0, description="最小长度")
    max_length: Optional[int] = Field(None, description="最大长度")
    allowed_languages: List[str] = Field(default=["zh-cn", "en"], description="允许的语言列表")

    @field_validator("text")
    @classmethod
    def validate_text_length(cls, v, info):
        min_length = info.data.get("min_length", 0)
        max_length = info.data.get("max_length")
        
        if len(v) < min_length:
            raise ValueError(f"文本长度不能小于{min_length}")
        if max_length and len(v) > max_length:
            raise ValueError(f"文本长度不能大于{max_length}")
        return v

    @field_validator("text")
    @classmethod
    def validate_language(cls, v, info):
        allowed_languages = info.data.get("allowed_languages", ["zh-cn", "en"])
        try:
            lang = langdetect.detect(v)
            if lang not in allowed_languages:
                raise ValueError(f"不支持的语言: {lang}")
        except langdetect.LangDetectException:
            raise ValueError("无法检测文本语言")
        return v

class ImageValidationModel(BaseValidationModel):
    """图像验证模型"""
    file_path: str = Field(..., description="图像文件路径")
    max_size_mb: float = Field(10.0, description="最大文件大小(MB)")
    min_width: int = Field(100, description="最小宽度")
    min_height: int = Field(100, description="最小高度")
    max_width: Optional[int] = Field(4096, description="最大宽度")
    max_height: Optional[int] = Field(4096, description="最大高度")
    allowed_formats: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif"],
        description="允许的图像格式"
    )

    @field_validator("file_path")
    @classmethod
    def validate_file_size(cls, v, info):
        max_size_mb = info.data.get("max_size_mb", 10.0)
        size_mb = os.path.getsize(v) / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(f"文件大小不能超过{max_size_mb}MB")
        return v

    @field_validator("file_path")
    @classmethod
    def validate_dimensions(cls, v, info):
        min_width = info.data.get("min_width", 100)
        min_height = info.data.get("min_height", 100)
        max_width = info.data.get("max_width")
        max_height = info.data.get("max_height")

        with Image.open(v) as img:
            width, height = img.size
            if width < min_width or height < min_height:
                raise ValueError(f"图像尺寸不能小于{min_width}x{min_height}")
            if max_width and width > max_width:
                raise ValueError(f"图像宽度不能大于{max_width}")
            if max_height and height > max_height:
                raise ValueError(f"图像高度不能大于{max_height}")
        return v

    @field_validator("file_path")
    @classmethod
    def validate_format(cls, v, info):
        allowed_formats = info.data.get("allowed_formats", ["image/jpeg", "image/png", "image/gif"])
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(v)
        if file_type not in allowed_formats:
            raise ValueError(f"不支持的图像格式: {file_type}")
        return v

class VideoValidationModel(BaseValidationModel):
    """视频验证模型"""
    file_path: str = Field(..., description="视频文件路径")
    max_duration_seconds: float = Field(300.0, description="最大时长(秒)")
    min_width: int = Field(320, description="最小宽度")
    min_height: int = Field(240, description="最小高度")
    max_width: Optional[int] = Field(3840, description="最大宽度")
    max_height: Optional[int] = Field(2160, description="最大高度")
    allowed_formats: List[str] = Field(
        default=["video/mp4", "video/avi", "video/mov"],
        description="允许的视频格式"
    )

    @field_validator("file_path")
    @classmethod
    def validate_duration(cls, v, info):
        max_duration = info.data.get("max_duration_seconds", 300.0)
        cap = cv2.VideoCapture(v)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        cap.release()
        
        if duration > max_duration:
            raise ValueError(f"视频时长不能超过{max_duration}秒")
        return v

    @field_validator("file_path")
    @classmethod
    def validate_resolution(cls, v, info):
        min_width = info.data.get("min_width", 320)
        min_height = info.data.get("min_height", 240)
        max_width = info.data.get("max_width")
        max_height = info.data.get("max_height")

        cap = cv2.VideoCapture(v)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        if width < min_width or height < min_height:
            raise ValueError(f"视频分辨率不能小于{min_width}x{min_height}")
        if max_width and width > max_width:
            raise ValueError(f"视频宽度不能大于{max_width}")
        if max_height and height > max_height:
            raise ValueError(f"视频高度不能大于{max_height}")
        return v

    @field_validator("file_path")
    @classmethod
    def validate_format(cls, v, info):
        allowed_formats = info.data.get("allowed_formats", ["video/mp4", "video/avi", "video/mov"])
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(v)
        if file_type not in allowed_formats:
            raise ValueError(f"不支持的视频格式: {file_type}")
        return v 