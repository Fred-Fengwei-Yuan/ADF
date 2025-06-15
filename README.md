# 算法服务框架

## 项目介绍

这是一个现代化的算法服务器部署框架，专为大规模AI算法服务设计。它提供了完整的API服务、并发管理、数据处理、服务注册和日志管理功能。采用Docker容器化部署，支持快速扩展和运维管理。

## 核心功能

### 1. API 服务
- 基于FastAPI框架，提供高性能的异步API服务
- 使用nginx反向代理，支持HTTP/HTTPS协议
- 同步 API：POST 请求直接返回结果
  - 适用于轻量级、快速响应的任务
  - 支持实时处理和数据校验
- 异步 API：提交任务后返回任务 ID，结果通过消息队列发送
  - 适用于耗时较长的任务
  - 支持任务状态查询和结果回调

### 2. 并发管理
- 接口并发：支持同时接收多个请求
  - 通过uvicorn配置控制最大并发数
  - 支持请求队列和超时处理
- 引擎并发：支持算法实例的独立控制
  - 可配置算法实例数量
  - 支持任务队列和负载均衡
  - 支持动态调整并发数

### 3. 数据处理
- 校验：
  - 参数校验
    - 必填项检查
    - 范围验证
  - 文本校验
    - 长度限制
    - 内容选项（对于选择型变量）
    - 语言识别
  - 图像校验
    - 存储大小
    - 图像尺寸
    - 格式
    - metadata
  - 视频校验
    - 存储大小
    - 画幅比例和尺寸
    - 格式
    - 时长
- 预处理：
  - 图像处理
    - 格式转换
    - 图像尺寸调整
  - 视频处理
    - 格式转换
- 后处理：
  - 结果格式化
  - 数据存储
    - 支持阿里云 OSS
    - 兼容 AWS S3
  - 结果回调

### 4. 服务注册
- 定期向上层系统发送HTTP方式的心跳机制
- 自动重连机制
- 服务状态监控
- 支持服务发现和负载均衡

### 5. 日志管理
- 服务日志（apiname.log）
  - API 请求和响应记录
  - 错误信息追踪
  - 性能指标统计
- 调试日志（apiname_debug.log）
  - 服务状态监控
  - 任务队列状态
  - 并发状态统计
  - 资源使用情况
- 日志轮转
  - 按大小和日期自动轮转
  - 日志压缩和归档
  - 日志清理策略

### 6. 环境变量控制
- 数据配置
  - 数据校验配置
  - 数据处理配置
- 部署配置
  - OSS配置
  - 消息队列配置
  - 数据库配置

## 环境依赖

### 基础依赖
- Python >= 3.11
- FastAPI >= 0.115.12
- FastMCP >= 2.8.1
- Uvicorn >= 0.34.3

### 数据处理
- Pillow (图像处理)
- OpenCV (视频处理)
- boto3 (OSS/S3支持)

### 消息队列
- RocketMQ
- Kafka

### 监控和日志
- Prometheus
- Grafana
- ELK Stack

## 快速开始

### 1. 环境准备
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
uv sync
```

### 2. 配置环境变量
```bash
cp .env
# 编辑.env文件，配置必要的环境变量
```

### 3. 本地开发
```bash
# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

### 4. Docker部署
```bash
# 构建镜像
docker build -t algorithm-service .

# 启动服务
docker-compose up -d

# 服务注册
docker exec algorithm-service python scripts/register_service.py
```

## API文档

启动服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 目录结构

```
.
├── app/                    # 应用主目录
│   ├── __init__.py
│   ├── main.py            # FastAPI应用入口
│   ├── data_processor.py   # 数据处理
│   ├── mq_client.py        # 消息队列客户端
│   ├── service_registry.py # 服务注册
│   ├── task_manager.py     # 任务队列管理 
│   └── utils/              # 工具函数
│       ├── logger_handler.py
│       ├── logger.py       # 日志工具
│       └── validator.py    # 数据验证
├── nginx/                  # Nginx配置
│   └── nginx.conf
├── gunicorn/               # Gunicorn配置
│   └── gunicorn.conf
├── scripts/                # 部署脚本
│   ├── deploy.sh
│   └── register_service.py
├── tests/                  # 测试用例
├── logs/                   # 日志目录
├── .env                    # 环境变量
├── pyproject.toml          # 项目配置
├── Dockerfile              # Docker构建文件
└── README.md               # 项目文档
```

## 开发计划

- [ ] 完善API文档
- [ ] 添加单元测试
- [ ] 实现监控面板
- [ ] 优化性能
- [ ] 添加更多数据处理功能
- [ ] 完善错误处理机制
- [ ] 添加性能测试
- [ ] 优化部署流程

## 贡献指南

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 作者：Fred Yuan
- 邮箱：cjcj188@gmail.com