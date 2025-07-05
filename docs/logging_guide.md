# 📝 API专用日志系统使用指南

## 🎯 概述

ADF框架提供了一个专为API设计的日志系统，**自动为每个API生成两类日志文件**：
- **服务日志**（`apiname.log`）：记录API的输入、输出和最终错误
- **调试日志**（`apiname_debug.log`）：记录服务状态、引擎状态变化和中间过程

这个系统将原来复杂的多套日志接口统一为简洁的API专用日志体系。

## ✨ 主要特性

- 🎯 **API专用**：每个API自动生成独立的日志文件
- 📁 **双日志分离**：服务日志和调试日志完全隔离
- 🔧 **自动管理**：无需手动配置，自动创建和管理日志文件
- 📊 **结构化日志**：支持额外字段记录
- 🚀 **高性能**：日志记录器缓存机制
- ☁️ **云端支持**：可选阿里云日志服务集成

## 🚀 快速开始

### 基础使用

```python
from app.utils import get_api_logger

# 获取API日志记录器
api_logger = get_api_logger("your_api_name")

# 服务日志 - 记录API输入输出
api_logger.service_info("API调用开始", extra_fields={"user_id": 123})
api_logger.service_info("API调用成功", extra_fields={"result": "success"})
api_logger.service_error("API调用失败", exc_info=exception)

# 调试日志 - 记录中间过程
api_logger.debug_info("开始数据处理", extra_fields={"step": "preprocessing"})
api_logger.debug_debug("中间变量", extra_fields={"temp_value": 456})
api_logger.debug_warning("引擎状态", extra_fields={"memory_usage": "85%"})
```

### 实际应用示例

```python
from app.utils import get_api_logger

class UserService:
    def __init__(self):
        self.logger = get_api_logger("user_service")
    
    def create_user(self, user_data):
        # 服务日志 - API输入
        self.logger.service_info("创建用户API调用", extra_fields={
            "user_data": str(user_data)[:200],  # 限制长度
            "request_id": "req_123"
        })
        
        # 调试日志 - 服务状态
        self.logger.debug_info("开始用户数据验证", extra_fields={
            "validation_step": "input_check"
        })
        
        try:
            # 业务逻辑
            validated_data = self._validate_user_data(user_data)
            
            # 调试日志 - 中间过程
            self.logger.debug_info("数据验证完成", extra_fields={
                "validation_result": "success",
                "validated_fields": list(validated_data.keys())
            })
            
            user = self._save_user(validated_data)
            
            # 服务日志 - API输出
            self.logger.service_info("创建用户成功", extra_fields={
                "user_id": user.id,
                "response_time": 1.5
            })
            
            return user
            
        except Exception as e:
            # 服务日志 - API错误
            self.logger.service_error("创建用户失败", extra_fields={
                "error_type": type(e).__name__,
                "error_message": str(e)
            }, exc_info=e)
            
            # 调试日志 - 错误详情
            self.logger.debug_error("用户创建过程中发生异常", extra_fields={
                "exception_details": str(e)
            }, exc_info=e)
            
            raise
```

## 📁 日志文件结构

### 自动生成的文件

```
logs/
├── user_api.log          # 用户API服务日志
├── user_api_debug.log    # 用户API调试日志
├── order_api.log         # 订单API服务日志
├── order_api_debug.log   # 订单API调试日志
├── payment_api.log       # 支付API服务日志
└── payment_api_debug.log # 支付API调试日志
```

### 日志内容示例

**服务日志** (`user_api.log`):
```
2025-06-29 18:14:23,875 - service.user_api - INFO - API调用开始
2025-06-29 18:14:23,876 - service.user_api - INFO - API调用成功
2025-06-29 18:14:23,877 - service.user_api - ERROR - API调用失败
```

**调试日志** (`user_api_debug.log`):
```
2025-06-29 18:14:23,877 - debug.user_api - INFO - 开始数据处理
2025-06-29 18:14:23,878 - debug.user_api - DEBUG - 中间变量值: 123
2025-06-29 18:14:23,879 - debug.user_api - WARNING - 引擎状态警告
```

## 🔧 日志级别

### 服务日志级别
- `service_info()` - 记录API输入、输出、成功信息
- `service_warning()` - 记录API警告信息
- `service_error()` - 记录API错误信息
- `service_critical()` - 记录API严重错误

### 调试日志级别
- `debug_debug()` - 记录详细的调试信息
- `debug_info()` - 记录一般调试信息
- `debug_warning()` - 记录调试警告
- `debug_error()` - 记录调试错误

## ⚙️ 配置选项

### 环境变量配置

在 `.env` 文件中配置：

```bash
# 日志级别配置
LOG_LEVEL=INFO                    # 全局日志级别

# 日志目录配置
LOG_DIR=logs                      # 日志文件目录

# 文件轮转配置
LOG_MAX_BYTES=10485760           # 单个日志文件最大大小（10MB）
LOG_BACKUP_COUNT=5               # 保留的日志文件数量

# 阿里云日志配置（可选）
ALIYUN_LOG_ENDPOINT=""           # 阿里云日志服务端点
ALIYUN_LOG_ACCESS_KEY_ID=""      # 访问密钥ID
ALIYUN_LOG_ACCESS_KEY_SECRET=""  # 访问密钥
ALIYUN_LOG_PROJECT=""            # 项目名称
ALIYUN_LOG_STORE=""              # 日志库名称
```

### 日志级别说明

- `DEBUG`：最详细的调试信息
- `INFO`：一般信息，记录程序正常运行状态
- `WARNING`：警告信息，可能的问题但不影响运行
- `ERROR`：错误信息，程序运行出错
- `CRITICAL`：严重错误，程序可能无法继续运行

## 🎯 最佳实践

### 1. API命名规范

```python
# 推荐：使用有意义的API名称
get_api_logger("user_management")
get_api_logger("order_processing")
get_api_logger("payment_gateway")

# 避免：使用过于简单的名称
get_api_logger("api")  # 不推荐
get_api_logger("test") # 不推荐
```

### 2. 日志内容规范

**服务日志**应该记录：
- API调用的输入参数（限制长度）
- API调用的输出结果（限制长度）
- 错误信息和异常
- 关键的业务状态变化

**调试日志**应该记录：
- 中间处理步骤
- 临时变量值
- 服务状态变化
- 引擎状态信息
- 性能指标

### 3. 结构化日志

```python
# 推荐：使用结构化字段
api_logger.service_info("用户登录", extra_fields={
    "user_id": 123,
    "login_method": "password",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
})

# 避免：将所有信息放在消息中
api_logger.service_info("用户123通过密码方式从192.168.1.1登录")  # 不推荐
```

### 4. 异常处理

```python
try:
    # 业务逻辑
    result = process_data(data)
except Exception as e:
    # 记录服务错误
    api_logger.service_error("数据处理失败", extra_fields={
        "error_type": type(e).__name__,
        "error_message": str(e)
    }, exc_info=e)
    
    # 记录调试错误
    api_logger.debug_error("处理过程中发生异常", extra_fields={
        "input_data": str(data)[:100],
        "exception_details": str(e)
    }, exc_info=e)
    
    raise
```

### 5. 性能考虑

```python
# 推荐：限制日志内容长度
api_logger.service_info("API调用", extra_fields={
    "input_data": str(data)[:500],  # 限制长度
    "output_data": str(result)[:500]  # 限制长度
})

# 避免：记录过大的数据
api_logger.service_info("API调用", extra_fields={
    "input_data": str(large_data),  # 可能很大
    "output_data": str(large_result)  # 可能很大
})
```

## 🔍 故障排除

### 常见问题

1. **日志文件不生成**
   - 检查 `LOG_DIR` 环境变量是否正确设置
   - 确保目录有写入权限
   - 检查是否有调用 `get_api_logger()`

2. **日志级别不生效**
   - 检查 `LOG_LEVEL` 环境变量是否正确设置
   - 重启应用使配置生效

3. **阿里云日志发送失败**
   - 检查网络连接
   - 验证访问密钥是否正确
   - 确认项目名称和日志库名称

### 调试技巧

```python
# 检查日志记录器状态
api_logger = get_api_logger("test_api")
print(f"API名称: {api_logger.api_name}")
print(f"日志级别: {api_logger.level}")

# 临时提高日志级别
import logging
api_logger.level = logging.DEBUG
```

## 📊 日志分析

### 查看特定API的日志

```bash
# 查看服务日志
tail -f logs/user_api.log

# 查看调试日志
tail -f logs/user_api_debug.log

# 搜索特定内容
grep "ERROR" logs/user_api.log
grep "user_id.*123" logs/user_api_debug.log
```

### 批量分析日志

```python
import os
import re

def analyze_api_logs(api_name):
    """分析指定API的日志"""
    service_log = f"logs/{api_name}.log"
    debug_log = f"logs/{api_name}_debug.log"
    
    # 统计错误数量
    error_count = 0
    if os.path.exists(service_log):
        with open(service_log, 'r') as f:
            for line in f:
                if 'ERROR' in line:
                    error_count += 1
    
    print(f"API {api_name} 错误数量: {error_count}")
```

## 🔮 高级功能

### 自定义日志格式

```python
# 在logger.py中可以自定义日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 日志轮转

系统自动支持日志轮转：
- 当日志文件达到 `LOG_MAX_BYTES` 大小时自动轮转
- 保留 `LOG_BACKUP_COUNT` 个备份文件
- 备份文件命名格式：`apiname.log.1`, `apiname.log.2` 等

### 阿里云日志集成

如果配置了阿里云日志服务，日志会自动发送到云端：
- 结构化JSON格式
- 支持日志查询和分析
- 支持告警和监控

## 📚 相关文档

- [Python logging 官方文档](https://docs.python.org/3/library/logging.html)
- [阿里云日志服务文档](https://help.aliyun.com/product/28958.html)
- [FastAPI 日志配置](https://fastapi.tiangolo.com/tutorial/logging/)

---

通过这个API专用日志系统，你可以轻松地为每个API维护独立的日志记录，实现服务日志和调试日志的完美分离，提高系统的可观测性和可维护性。 