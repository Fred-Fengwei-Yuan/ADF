#!/usr/bin/env python3
"""
API日志系统测试脚本
~~~~~~~~~~~~~~~~~

用于测试新的API日志系统，验证服务日志和调试日志的分离功能。
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils import get_api_logger

def test_api_logger_basic():
    """测试API日志记录器基础功能"""
    print("=== 测试API日志记录器基础功能 ===")
    
    # 创建API日志记录器
    api_logger = get_api_logger("test_api")
    
    # 测试服务日志
    api_logger.service_info("API调用开始", extra_fields={
        "user_id": 123,
        "request_id": "req_456",
        "endpoint": "/api/v1/test"
    })
    
    api_logger.service_warning("API调用警告", extra_fields={
        "user_id": 123,
        "warning_type": "rate_limit"
    })
    
    api_logger.service_error("API调用失败", extra_fields={
        "user_id": 123,
        "error_code": 500,
        "error_message": "Internal server error"
    }, exc_info=Exception("模拟异常"))
    
    # 测试调试日志
    api_logger.debug_debug("开始数据处理", extra_fields={
        "step": "preprocessing",
        "data_size": 1024
    })
    
    api_logger.debug_info("数据处理完成", extra_fields={
        "step": "preprocessing",
        "processing_time": 1.5,
        "output_size": 512
    })
    
    api_logger.debug_warning("引擎状态警告", extra_fields={
        "engine": "ml_engine",
        "warning": "high_memory_usage",
        "memory_usage": "85%"
    })

def test_multiple_apis():
    """测试多个API的日志分离"""
    print("\n=== 测试多个API的日志分离 ===")
    
    # 创建多个API日志记录器
    user_api_logger = get_api_logger("user_api")
    order_api_logger = get_api_logger("order_api")
    payment_api_logger = get_api_logger("payment_api")
    
    # 用户API日志
    user_api_logger.service_info("用户登录", extra_fields={
        "user_id": 123,
        "login_method": "password"
    })
    
    user_api_logger.debug_info("用户认证过程", extra_fields={
        "auth_step": "password_verification",
        "auth_time": 0.5
    })
    
    # 订单API日志
    order_api_logger.service_info("创建订单", extra_fields={
        "user_id": 123,
        "order_id": "order_789",
        "amount": 99.99
    })
    
    order_api_logger.debug_info("订单处理过程", extra_fields={
        "step": "inventory_check",
        "available": True
    })
    
    # 支付API日志
    payment_api_logger.service_info("支付处理", extra_fields={
        "user_id": 123,
        "order_id": "order_789",
        "payment_method": "credit_card"
    })
    
    payment_api_logger.debug_info("支付验证", extra_fields={
        "step": "card_verification",
        "verification_time": 2.1
    })

def test_logger_cache():
    """测试日志记录器缓存功能"""
    print("\n=== 测试日志记录器缓存功能 ===")
    
    # 获取同一个API的日志记录器两次
    logger1 = get_api_logger("cache_test")
    logger2 = get_api_logger("cache_test")
    
    print(f"logger1 和 logger2 是同一个对象: {logger1 is logger2}")
    
    # 测试服务日志
    logger1.service_info("来自logger1的服务日志")
    logger2.service_info("来自logger2的服务日志")
    
    # 测试调试日志
    logger1.debug_info("来自logger1的调试日志")
    logger2.debug_info("来自logger2的调试日志")

def test_log_files():
    """检查生成的日志文件"""
    print("\n=== 检查生成的日志文件 ===")
    
    logs_dir = os.getenv('LOG_DIR', 'logs')
    
    if os.path.exists(logs_dir):
        print(f"日志目录: {logs_dir}")
        files = os.listdir(logs_dir)
        
        # 按API分组显示文件
        api_files = {}
        for file in files:
            if file.endswith('.log'):
                if '_debug.log' in file:
                    api_name = file.replace('_debug.log', '')
                    if api_name not in api_files:
                        api_files[api_name] = {'service': None, 'debug': None}
                    api_files[api_name]['debug'] = file
                else:
                    api_name = file.replace('.log', '')
                    if api_name not in api_files:
                        api_files[api_name] = {'service': None, 'debug': None}
                    api_files[api_name]['service'] = file
        
        for api_name, files_dict in api_files.items():
            print(f"\nAPI: {api_name}")
            print(f"  服务日志: {files_dict['service'] or '未生成'}")
            print(f"  调试日志: {files_dict['debug'] or '未生成'}")
            
            # 显示文件大小
            if files_dict['service']:
                service_path = os.path.join(logs_dir, files_dict['service'])
                size = os.path.getsize(service_path)
                print(f"  服务日志大小: {size} bytes")
            
            if files_dict['debug']:
                debug_path = os.path.join(logs_dir, files_dict['debug'])
                size = os.path.getsize(debug_path)
                print(f"  调试日志大小: {size} bytes")
    else:
        print(f"日志目录不存在: {logs_dir}")

def main():
    """主测试函数"""
    print("🚀 开始测试API日志系统")
    print("=" * 60)
    
    try:
        test_api_logger_basic()
        test_multiple_apis()
        test_logger_cache()
        test_log_files()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("\n📝 API日志系统功能说明：")
        print("1. 自动生成服务日志文件: {api_name}.log")
        print("2. 自动生成调试日志文件: {api_name}_debug.log")
        print("3. 服务日志记录API输入输出和错误")
        print("4. 调试日志记录服务状态、引擎状态和中间过程")
        print("5. 支持结构化日志和额外字段")
        print("6. 日志记录器缓存机制")
        print("7. 文件轮转和大小控制")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 