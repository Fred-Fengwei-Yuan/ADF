from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ValidationRule:
    """验证规则数据类"""
    required: bool
    type: type
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    choices: Optional[List[Any]] = None
    regex: Optional[str] = None

class Validator:
    """数据验证工具"""
    
    def validate_param(self, data: Dict[str, Any], rules: Dict[str, ValidationRule]) -> bool:
        """验证参数"""
        pass
        
    def validate_text(self, text: str, max_length: Optional[int] = None, 
                     choices: Optional[List[str]] = None) -> bool:
        """验证文本"""
        pass
        
    def validate_image(self, image_data: bytes, max_size: int, 
                      min_width: int, min_height: int) -> bool:
        """验证图像"""
        pass
        
    def validate_video(self, video_data: bytes, max_size: int, 
                      max_duration: int) -> bool:
        """验证视频"""
        pass
        
    def validate_format(self, data: bytes, allowed_formats: List[str]) -> bool:
        """验证格式"""
        pass
