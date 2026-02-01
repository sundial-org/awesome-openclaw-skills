#!/usr/bin/env python3
"""
飞书文档Blocks获取工具 - 专门用于获取文档的完整blocks结构
根据飞书官方API文档实现，确保获取完整的文档详细内容
"""

import os
import sys
import json
import requests
from typing import Optional, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class FeishuDocBlocksReader:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = None
        
    def get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        if self.tenant_access_token:
            return self.tenant_access_token
            
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") != 0:
                raise Exception(f"认证失败: {data.get('msg', 'Unknown error')}")
                
            self.tenant_access_token = data["tenant_access_token"]
            logger.info("成功获取访问令牌")
            return self.tenant_access_token
            
        except Exception as e:
            raise Exception(f"获取访问令牌失败: {e}")
    
    def get_document_info(self, doc_token: str) -> Dict[str, Any]:
        """获取文档基本信息"""
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}"
        headers = {
            "Authorization": f"Bearer {self.get_tenant_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"获取文档信息失败: {data.get('msg', 'Unknown error')} (code: {data.get('code')})")
                
            return data["data"]
            
        except Exception as e:
            raise Exception(f"获取文档信息失败: {e}")
    
    def get_document_blocks(self, doc_token: str) -> Dict[str, Any]:
        """获取文档的完整blocks结构 - 这是核心功能"""
        # 首先获取文档信息以确认文档存在
        doc_info = self.get_document_info(doc_token)
        
        # 获取完整的blocks
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks"
        headers = {
            "Authorization": f"Bearer {self.get_tenant_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"获取文档blocks失败: {data.get('msg', 'Unknown error')} (code: {data.get('code')})")
                
            blocks_data = data["data"]
            logger.info(f"成功获取文档blocks，共 {len(blocks_data.get('blocks', {}))} 个块")
            return blocks_data
            
        except Exception as e:
            raise Exception(f"获取文档blocks失败: {e}")
    
    def get_complete_document(self, doc_token: str) -> Dict[str, Any]:
        """获取完整的文档信息，包括元数据和所有blocks"""
        try:
            # 获取文档基本信息
            doc_info = self.get_document_info(doc_token)
            
            # 获取完整的blocks结构
            blocks_data = self.get_document_blocks(doc_token)
            
            # 合并结果
            result = {
                "document_info": doc_info,
                "blocks": blocks_data.get("blocks", {}),
                "block_order": blocks_data.get("block_order", [])
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"获取完整文档失败: {e}")

def load_config():
    """从配置文件加载App ID和App Secret"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    config_paths = [
        "./reference/feishu_config.json",
        os.path.join(project_root, "reference", "feishu_config.json"),
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                app_id = config.get("app_id")
                app_secret = config.get("app_secret")
                
                if app_id and app_secret:
                    logger.info(f"从 {config_path} 加载配置")
                    return app_id, app_secret
                    
            except Exception as e:
                logger.warning(f"从 {config_path} 加载配置失败: {e}")
                continue
    
    # 如果配置文件不存在，尝试从环境变量获取
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    
    if app_id and app_secret:
        logger.info("从环境变量加载配置")
        return app_id, app_secret
    
    raise Exception("未找到有效的配置文件或环境变量")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python get_feishu_doc_blocks.py <document_token>")
        print("\n示例:")
        print("  python get_feishu_doc_blocks.py docx_AbCdEfGhIjKlMnOpQrStUv")
        sys.exit(1)
    
    doc_token = sys.argv[1]
    
    try:
        # 加载配置
        app_id, app_secret = load_config()
        reader = FeishuDocBlocksReader(app_id, app_secret)
        
        logger.info(f"正在获取文档 {doc_token} 的完整blocks结构...")
        
        # 获取完整文档
        complete_doc = reader.get_complete_document(doc_token)
        
        # 输出JSON格式的结果
        print(json.dumps(complete_doc, ensure_ascii=False, indent=2))
        
    except KeyboardInterrupt:
        logger.info("操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()