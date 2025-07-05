# 🚀 ADF - 算法服务部署框架

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.12-green.svg)](https://fastapi.tiangolo.com/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.8.1-green.svg)](https://gofastmcp.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个现代化的算法服务部署框架，让算法服务部署变得简单高效 ✨

</div>

## 📖 简介

ADF是一个专为AI算法服务设计的现代化框架。它就像是一个智能工厂，可以帮你：

- 🎯 快速部署算法服务
- 🔄 高效处理数据
- 📊 智能管理任务
- 📈 实时监控性能

无论你是想部署一个简单的图像识别服务，还是构建一个复杂的视频分析系统，ADF都能帮你轻松搞定！

## ✨ 主要特点

### 1️⃣ 智能API服务
- 🚀 高性能异步处理
- 🔄 支持同步和异步两种模式
- 📱 提供RESTful API和命令行工具
- 🔌 支持多种数据格式

### 2️⃣ 强大的数据处理
- 🖼️ 图像处理
  - 格式转换
  - 尺寸调整
  - 数据增强
  - 智能优化
- 🎥 视频处理
  - 格式转换
  - 帧率调整
  - 分辨率优化
  - 关键帧提取
- 📊 数据验证
  - 智能校验
  - 格式检查
  - 质量评估

### 3️⃣ 智能任务管理
- 📋 任务队列
- ⚖️ 负载均衡
- 🔄 自动重试
- 📊 状态监控

### 4️⃣ 完善的监控系统
- 📈 性能监控
- 🔍 错误追踪
- 📊 资源使用统计
- 📝 详细日志记录

### 5️⃣ 统一日志系统
- 🖥️ 控制台输出
- 📁 文件轮转
- ☁️ 阿里云日志服务
- 🔧 灵活配置
- 📊 结构化日志

### 6️⃣ 模块化设计
- 🔌 **可插拔组件**: 日志、消息队列、存储等核心组件均可独立配置、替换或禁用。
- ⚙️ **环境变量驱动**: 通过环境变量即可轻松切换组件实现，无需修改代码。
- 🧱 **易于扩展**: 提供清晰的基类和工厂模式，方便开发者快速集成新的服务。

## 🛠️ 技术栈

- **后端框架**: FastAPI, FastMCP
- **数据处理**: OpenCV, Pillow, NumPy
- **存储系统**: MySQL, Redis
- **消息队列**: RocketMQ, Kafka, RabbitMQ
- **日志服务**: 内置Logging, Loguru, 阿里云日志服务
- **监控工具**: Prometheus, Grafana
- **容器化**: Docker

## 🚀 快速开始

### 1. 安装
```bash
# 克隆项目
git clone https://github.com/fred-fengwei-yuan/adf.git
cd adf

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

### 2. 配置

```bash
# 复制配置文件
cp env.example .env

# 编辑配置文件
vim .env
```

### 3. 运行

```bash
# 方式1: 使用启动脚本（推荐）
python start_server.py

# 方式2: 直接使用uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 方式3: 使用Docker
docker build -t adf .
docker run -p 8000:8000 adf
```

### 4. 访问

打开浏览器访问：
- API文档: http://localhost:8000/docs
- 监控面板: http://localhost:3000

## 📝 日志系统使用

### 基础使用
```python
from app.utils import get_logger

logger = get_logger(__name__)
logger.info("这是一条信息日志")
logger.error("这是一条错误日志")
```

### 服务日志
```python
from app.utils import get_service_logger

service_logger = get_service_logger("api")
service_logger.info("API请求处理完成", extra_fields={"user_id": 123})
```

### 调试日志
```python
from app.utils import get_debug_logger

debug_logger = get_debug_logger("data_processing")
debug_logger.debug("数据处理步骤", extra_fields={"step": "preprocessing"})
```

### 环境变量配置
```bash
# 日志级别配置
LOG_LEVEL=INFO                    # 全局日志级别
CONSOLE_LOG_LEVEL=INFO           # 控制台日志级别
FILE_LOG_LEVEL=DEBUG             # 文件日志级别
ALIYUN_LOG_LEVEL=INFO            # 阿里云日志级别

# 文件日志配置
LOG_FILE=logs/app.log            # 日志文件路径
LOG_MAX_BYTES=10485760          # 单个日志文件最大大小（10MB）
LOG_BACKUP_COUNT=5              # 保留的日志文件数量

# 阿里云日志配置
ALIYUN_LOG_ENDPOINT=""          # 阿里云日志服务端点
ALIYUN_LOG_ACCESS_KEY_ID=""     # 访问密钥ID
ALIYUN_LOG_ACCESS_KEY_SECRET="" # 访问密钥
ALIYUN_LOG_PROJECT=""           # 项目名称
ALIYUN_LOG_STORE=""             # 日志库名称
```

## 🤝 贡献指南

我们欢迎任何形式的贡献！无论是：

- 🐛 报告问题
- 💡 提出建议
- 🔧 修复bug
- ✨ 添加新功能

请查看我们的[贡献指南](CONTRIBUTING.md)了解更多信息。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系我们

- 💬 问题反馈: [GitHub Issues](https://github.com/yourusername/adf/issues)
- 📧 邮件联系: cjcj188@gmail.com
- 💻 作者: Fred Yuan

## 🌟 致谢

感谢所有为这个项目做出贡献的开发者！

---

<div align="center">

**ADF** ©2025 Created by Fred Yuan

</div>

## ⚙️ 并发配置

ADF支持两种并发模式，可以独立配置：

### 1. API服务并发（接口并发）
- **配置项**: `API_WORKERS`
- **默认值**: 4
- **作用**: 控制FastAPI服务的工作进程数
- **使用方式**: `uvicorn app.main:app --workers 4`

### 2. 算法引擎并发（引擎并发）
- **配置项**: `ENGINE_WORKERS`
- **默认值**: 2
- **作用**: 控制算法模型的工作线程数
- **特点**: 任务在队列中排队，由引擎并发处理

### 3. 并发配置示例

```bash
# 环境变量配置
API_WORKERS=4          # 4个API工作进程
ENGINE_WORKERS=2       # 2个算法引擎线程
TASK_QUEUE_SIZE=1000   # 任务队列最大1000个任务

# 启动命令
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 并发监控

```bash
# 查看队列统计信息
curl http://localhost:8000/api/v1/queue/stats

# 返回示例
{
  "queue_size": 5,
  "max_queue_size": 1000,
  "active_workers": 2,
  "max_workers": 2,
  "total_tasks": 150,
  "is_started": true
}
```

## ⚙️ 核心模块配置

ADF框架的核心功能均可通过环境变量进行模块化配置，让你能根据不同部署环境和需求，自由组合功能。

### 1. 日志系统 (`LOG_TYPE`)

控制日志的记录方式。

- **`LOG_TYPE`**: `logging` (默认), `loguru`, `aliyun`, `none`
  - `logging`: 使用Python内置的`logging`模块，支持控制台和文件输出。
  - `loguru`: 使用`Loguru`库，提供更强大、更易用的日志记录功能。
  - `aliyun`: 对接到阿里云日志服务SLS。
  - `none`: 关闭日志记录功能。

**示例 (`.env`文件):**
```bash
# 选择Loguru作为日志系统
LOG_TYPE=loguru
```

### 2. 消息队列 (`MQ_TYPE`)

用于任务异步处理和系统解耦。

- **`MQ_TYPE`**: `kafka`, `rocketmq`, `rabbitmq`, `none` (默认)
  - `kafka`, `rocketmq`, `rabbitmq`: 选择对应的消息队列服务。
  - `none`: 禁用消息队列功能。异步任务的回调等功能将不可用。

**示例 (`.env`文件):**
```bash
# 选择RabbitMQ作为消息队列
MQ_TYPE=rabbitmq
MQ_HOST=localhost
MQ_PORT=5672
```

### 3. 存储服务 (`STORAGE_TYPE`)

用于处理结果的持久化存储，如上传到云存储。

- **`STORAGE_TYPE`**: `oss` (阿里云OSS), `none` (默认)
  - `oss`: 将文件上传到阿里云对象存储服务。
  - `none`: 禁用上传功能，处理结果只通过API返回。

**示例 (`.env`文件):**
```bash
# 启用阿里云OSS上传
STORAGE_TYPE=oss
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=your_bucket_name
```

### 4. 数据处理参数

通过环境变量控制数据预处理的行为，无需修改代码。

- `PREPROCESS_MAX_IMAGE_WIDTH`: 允许处理的最大图片宽度 (例如: `1920`)。
- `PREPROCESS_MAX_IMAGE_HEIGHT`: 允许处理的最大图片高度 (例如: `1080`)。
- `PREPROCESS_MAX_VIDEO_SECONDS`: 允许处理的最大视频时长，单位为秒 (例如: `60`)。

**示例 (`.env`文件):**
```bash
# 限制图片最大为1920x1080
PREPROCESS_MAX_IMAGE_WIDTH=1920
PREPROCESS_MAX_IMAGE_HEIGHT=1080
```
