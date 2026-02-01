#!/usr/bin/env python3
"""
飞书文档读取工具 - 优化版本
支持读取飞书文档（Docx/Doc）和表格（Sheet）的内容
提供更好的错误处理、安全性和用户体验
"""

import os
import sys
import json
import requests
from typing import Optional, Dict, Any, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class FeishuDocReader:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = None
        self.token_expires_in = 0
        
    def get_tenant_access_token(self) -> str:
        """获取租户访问令牌，支持缓存和刷新"""
        # 这里简化处理，实际应用中可以添加过期时间检查
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
            self.token_expires_in = data.get("expire", 7200)  # 默认2小时
            logger.info("成功获取访问令牌")
            return self.tenant_access_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {e}")
        except Exception as e:
            raise Exception(f"获取访问令牌失败: {e}")
    
    def _make_request(self, url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """通用请求方法，处理认证和错误"""
        token = self.get_tenant_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=15, **kwargs)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, timeout=15, **kwargs)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
                
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != 0:
                msg = data.get("msg", "Unknown error")
                error_code = data.get("code")
                # 提供更友好的错误信息
                if error_code == 94999:
                    raise Exception(f"文档不存在或无访问权限 (错误码: {error_code})")
                elif error_code == 10002:
                    raise Exception(f"应用权限不足，请检查应用是否已授权相应权限 (错误码: {error_code})")
                else:
                    raise Exception(f"API调用失败: {msg} (错误码: {error_code})")
                    
            return data["data"]
            
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise Exception("网络连接失败，请检查网络设置")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("认证失败，请检查App ID和App Secret是否正确")
            elif e.response.status_code == 403:
                raise Exception("权限不足，请确保应用已获得相应权限且文档已共享给应用")
            elif e.response.status_code == 404:
                raise Exception("文档未找到，请检查文档Token是否正确")
            else:
                raise Exception(f"HTTP错误: {e.response.status_code}")
        except json.JSONDecodeError:
            raise Exception("服务器返回了无效的JSON响应")
    
    def get_doc_info(self, doc_token: str) -> Dict[str, Any]:
        """获取飞书文档基本信息"""
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}"
        return self._make_request(url)
    
    def get_doc_blocks(self, doc_token: str) -> Dict[str, Any]:
        """获取飞书文档的块内容（完整内容结构）"""
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks"
        return self._make_request(url)
    
    def get_doc_content_simple(self, doc_token: str) -> str:
        """获取文档的简化文本内容（仅文本，无格式）"""
        blocks = self.get_doc_blocks(doc_token)
        return self._extract_text_from_blocks(blocks.get("blocks", {}))
    
    def _extract_text_from_blocks(self, blocks: Dict[str, Any]) -> str:
        """从块数据中提取纯文本内容"""
        text_parts = []
        
        def process_block(block):
            block_type = block.get("block_type", "")
            if block_type == "text":
                text_elements = block.get("text", {}).get("elements", [])
                for element in text_elements:
                    if element.get("type") == "text_run":
                        text_parts.append(element.get("text_run", {}).get("content", ""))
                    elif element.get("type") == "mention_user":
                        user_info = element.get("mention_user", {})
                        text_parts.append(f"@{user_info.get('name', user_info.get('user_id', 'unknown'))}")
            elif block_type == "heading1":
                text_parts.append("# " + self._extract_text_from_elements(block.get("heading1", {}).get("elements", [])))
            elif block_type == "heading2":
                text_parts.append("## " + self._extract_text_from_elements(block.get("heading2", {}).get("elements", [])))
            elif block_type == "heading3":
                text_parts.append("### " + self._extract_text_from_elements(block.get("heading3", {}).get("elements", [])))
            elif block_type == "bullet":
                text_parts.append("- " + self._extract_text_from_elements(block.get("bullet", {}).get("elements", [])))
            elif block_type == "ordered":
                text_parts.append("1. " + self._extract_text_from_elements(block.get("ordered", {}).get("elements", [])))
            elif block_type == "quote":
                text_parts.append("> " + self._extract_text_from_elements(block.get("quote", {}).get("elements", [])))
            elif block_type == "equation":
                equation = block.get("equation", {}).get("expression", "")
                text_parts.append(f"$$${equation}$$$")
            elif block_type == "table":
                # 简单处理表格
                table_cells = block.get("table", {}).get("cells", {})
                if table_cells:
                    text_parts.append("[表格内容]")
            
            # 处理子块
            children = block.get("children", [])
            for child_id in children:
                if child_id in blocks:
                    process_block(blocks[child_id])
        
        # 找到根块（通常第一个块是根）
        if blocks:
            root_block_id = next(iter(blocks))
            process_block(blocks[root_block_id])
        
        return "\n".join(text_parts)
    
    def _extract_text_from_elements(self, elements: List[Dict]) -> str:
        """从文本元素中提取纯文本"""
        text_parts = []
        for element in elements:
            if element.get("type") == "text_run":
                text_parts.append(element.get("text_run", {}).get("content", ""))
            elif element.get("type") == "mention_user":
                user_info = element.get("mention_user", {})
                text_parts.append(f"@{user_info.get('name', user_info.get('user_id', 'unknown'))}")
        return "".join(text_parts)
    
    def get_sheet_info(self, sheet_token: str) -> Dict[str, Any]:
        """获取飞书表格基本信息"""
        url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{sheet_token}"
        return self._make_request(url)
    
    def get_sheet_values(self, sheet_token: str, range_name: Optional[str] = None) -> Dict[str, Any]:
        """获取飞书表格的值"""
        if range_name:
            url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{sheet_token}/values/{range_name}"
        else:
            url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{sheet_token}/values"
        return self._make_request(url)
    
    def list_sheet_titles(self, sheet_token: str) -> List[str]:
        """获取表格中所有工作表的标题"""
        sheet_info = self.get_sheet_info(sheet_token)
        sheets = sheet_info.get("sheets", [])
        return [sheet.get("title", f"Sheet{i}") for i, sheet in enumerate(sheets)]

def load_config():
    """从 ./reference/feishu_config.json 文件加载配置"""
    # 首先尝试当前工作目录下的 reference 目录
    config_file = "./reference/feishu_config.json"
    
    # 如果不存在，尝试相对于脚本位置的 reference 目录
    if not os.path.exists(config_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(script_dir, "..", "reference", "feishu_config.json")
    
    # 如果还不存在，尝试从环境变量获取
    if not os.path.exists(config_file):
        app_id = os.getenv("FEISHU_APP_ID")
        app_secret = os.getenv("FEISHU_APP_SECRET")
        if app_id and app_secret:
            logger.info("从环境变量加载配置")
            return app_id, app_secret
    
    if not os.path.exists(config_file):
        raise Exception(f"配置文件不存在: ./reference/feishu_config.json (尝试了多个位置)")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        app_id = config.get("app_id")
        app_secret = config.get("app_secret")
        
        if not app_id or not app_secret:
            raise Exception(f"配置文件 {config_file} 缺少必要的 app_id 或 app_secret 字段")
        
        logger.info(f"从 {config_file} 加载配置")
        return app_id, app_secret
        
    except json.JSONDecodeError as e:
        raise Exception(f"配置文件 {config_file} 格式无效: {e}")
    except Exception as e:
        raise Exception(f"加载配置文件失败: {e}")

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python read_feishu_doc.py <document_token> [选项]")
        print("\n选项:")
        print("  --type doc|sheet        文档类型 (默认: auto)")
        print("  --format full|simple    输出格式 (默认: full)")
        print("  --sheet-title TITLE     指定工作表标题 (用于表格)")
        print("  --range RANGE           指定范围 (用于表格，如 A1:C10)")
        print("\n示例:")
        print("  python read_feishu_doc.py docx_xxxxxxxxxxxxxxx")
        print("  python read_feishu_doc.py sheet_xxxxxxxxxxxxxxx --type sheet --format simple")
        sys.exit(1)
    
    doc_token = sys.argv[1]
    doc_type = "auto"
    output_format = "full"
    sheet_title = None
    range_name = None
    
    # 解析命令行参数
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--type" and i + 1 < len(sys.argv):
            doc_type = sys.argv[i + 1]
            i += 2
        elif arg == "--format" and i + 1 < len(sys.argv):
            output_format = sys.argv[i + 1]
            i += 2
        elif arg == "--sheet-title" and i + 1 < len(sys.argv):
            sheet_title = sys.argv[i + 1]
            i += 2
        elif arg == "--range" and i + 1 < len(sys.argv):
            range_name = sys.argv[i + 1]
            i += 2
        else:
            print(f"未知参数: {arg}")
            sys.exit(1)
    
    try:
        # 加载配置
        app_id, app_secret = load_config()
        if not app_id or not app_secret:
            raise Exception("缺少必要的配置参数")
        
        reader = FeishuDocReader(app_id, app_secret)
        
        # 自动检测文档类型
        if doc_type == "auto":
            if doc_token.startswith("docx_"):
                doc_type = "doc"
            elif doc_token.startswith("sheet_"):
                doc_type = "sheet"
            else:
                # 尝试作为文档处理
                doc_type = "doc"
        
        logger.info(f"正在读取 {doc_type} 文档: {doc_token}")
        
        if doc_type == "sheet":
            if output_format == "simple":
                # 获取表格基本信息
                sheet_info = reader.get_sheet_info(doc_token)
                titles = reader.list_sheet_titles(doc_token)
                result = {
                    "type": "sheet",
                    "title": sheet_info.get("title", "Unknown"),
                    "sheet_titles": titles,
                    "total_sheets": len(titles)
                }
            else:
                # 获取完整表格数据
                if sheet_title:
                    # 需要先获取工作表ID
                    sheet_info = reader.get_sheet_info(doc_token)
                    sheet_id = None
                    for sheet in sheet_info.get("sheets", []):
                        if sheet.get("title") == sheet_title:
                            sheet_id = sheet.get("sheetId")
                            break
                    if sheet_id:
                        range_name = f"'{sheet_title}'!{range_name}" if range_name else sheet_id
                    else:
                        logger.warning(f"未找到工作表 '{sheet_title}'，使用默认范围")
                
                values = reader.get_sheet_values(doc_token, range_name)
                result = {
                    "type": "sheet",
                    "values": values
                }
        else:
            # 文档处理
            if output_format == "simple":
                content = reader.get_doc_content_simple(doc_token)
                result = {
                    "type": "doc",
                    "content": content
                }
            else:
                doc_info = reader.get_doc_info(doc_token)
                blocks = reader.get_doc_blocks(doc_token)
                result = {
                    "type": "doc",
                    "document": doc_info,
                    "blocks": blocks
                }
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except KeyboardInterrupt:
        logger.info("操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()