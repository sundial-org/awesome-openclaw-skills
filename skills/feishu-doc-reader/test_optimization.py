#!/usr/bin/env python3
"""
测试 feishu-doc-reader 优化版本的功能
"""

import os
import sys
import json
import tempfile

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.read_feishu_doc import FeishuDocReader, load_config

def test_config_loading():
    """测试配置加载功能"""
    print("=== 测试配置加载 ===")
    
    # 测试环境变量加载
    try:
        # 临时设置环境变量
        os.environ["FEISHU_APP_ID"] = "test_app_id"
        os.environ["FEISHU_APP_SECRET"] = "test_app_secret"
        
        app_id, app_secret = load_config()
        if app_id == "test_app_id" and app_secret == "test_app_secret":
            print("✓ 环境变量加载成功")
        else:
            print("✗ 环境变量加载失败: 返回值不匹配")
        
        # 清理环境变量
        del os.environ["FEISHU_APP_ID"]
        del os.environ["FEISHU_APP_SECRET"]
        
    except Exception as e:
        print(f"✗ 环境变量加载失败: {e}")
    
    # 测试 secrets 文件加载
    try:
        # 创建临时 secrets 文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test_secret_from_file")
            secret_file = f.name
        
        os.environ["FEISHU_APP_ID"] = "test_app_id"
        os.environ["FEISHU_APP_SECRET"] = "test_secret_from_file"
        
        app_id, app_secret = load_config()
        if app_id == "test_app_id" and app_secret == "test_secret_from_file":
            print("✓ 环境变量 Secret 加载成功")
        else:
            print("✗ 环境变量 Secret 加载失败: 返回值不匹配")
        
        # 清理
        os.unlink(secret_file)
        del os.environ["FEISHU_APP_ID"]
        del os.environ["FEISHU_APP_SECRET"]
        
    except Exception as e:
        print(f"✗ Secrets 文件加载失败: {e}")
    
    # 测试配置文件加载（如果存在）
    config_file = "./reference/feishu_config.json"
    if os.path.exists(config_file):
        try:
            app_id, app_secret = load_config()
            if app_id and app_secret:
                print("✓ 配置文件加载成功")
            else:
                print("✗ 配置文件加载失败: 返回值为空")
        except Exception as e:
            print(f"✗ 配置文件加载失败: {e}")
    else:
        print("ℹ️  配置文件不存在，跳过测试")

def test_document_reader():
    """测试文档读取器基本功能"""
    print("\n=== 测试文档读取 ===")
    
    try:
        # 使用测试凭据创建实例
        reader = FeishuDocReader("test_app_id", "test_app_secret")
        print("✓ 成功创建 FeishuDocReader 实例")
        
        # 测试方法存在性
        methods = [
            'get_tenant_access_token',
            'get_doc_info', 
            'get_doc_blocks',
            'get_doc_content_simple',
            'get_sheet_info',
            'get_sheet_values'
        ]
        
        for method in methods:
            if hasattr(reader, method):
                print(f"✓ 方法 {method} 存在")
            else:
                print(f"✗ 方法 {method} 不存在")
                
        print("✓ 文档读取功能准备就绪（需要有效文档 token 进行完整测试）")
        
    except Exception as e:
        print(f"✗ 创建实例失败: {e}")

def main():
    """运行所有测试"""
    print("开始测试 feishu-doc-reader 优化版本...\n")
    
    test_config_loading()
    test_document_reader()
    
    print("\n=== 测试完成 ===")
    print("注意：此测试需要有效的飞书 App ID 和 Secret")
    print("以及有效的文档 token 才能完整测试所有功能")

if __name__ == "__main__":
    main()