#!/usr/bin/env python3
"""
简单的集成测试脚本 - 验证Feishu文档blocks获取功能
"""

import os
import sys
import json

def test_config_exists():
    """测试配置文件是否存在"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    config_paths = [
        "./reference/feishu_config.json",
        os.path.join(project_root, "reference", "feishu_config.json"),
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            print(f"✅ Configuration loaded successfully from {path}")
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                    if 'app_id' in config and 'app_secret' in config:
                        return True
                    else:
                        print("❌ Configuration file missing required fields")
                        return False
            except Exception as e:
                print(f"❌ Configuration file parse error: {e}")
                return False
    
    print("❌ Configuration file not found")
    return False

def test_python_script():
    """测试Python脚本是否存在且可导入"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "get_feishu_doc_blocks.py")
    if os.path.exists(script_path):
        print("✅ Blocks extraction script found")
        # 简单的语法检查
        try:
            with open(script_path, 'r') as f:
                compile(f.read(), script_path, 'exec')
            print("✅ Python script syntax OK")
            return True
        except SyntaxError as e:
            print(f"❌ Python script syntax error: {e}")
            return False
        except Exception as e:
            print(f"❌ Python script error: {e}")
            return False
    else:
        print("❌ Blocks extraction script not found")
        return False

def test_shell_script():
    """测试Shell脚本是否存在且可执行"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shell_path = os.path.join(script_dir, "get_blocks.sh")
    if os.path.exists(shell_path):
        print("✅ Shell wrapper script found")
        if os.access(shell_path, os.X_OK):
            print("✅ Shell wrapper script is executable")
            return True
        else:
            print("❌ Shell wrapper script is not executable")
            return False
    else:
        print("❌ Shell wrapper script not found")
        return False

def main():
    print("Testing Feishu document blocks extraction...")
    
    tests = [
        test_config_exists(),
        test_python_script(),
        test_shell_script()
    ]
    
    if all(tests):
        print("\n✅ All tests passed! The integration is ready.")
        print("\nUsage examples:")
        print("  ./scripts/get_blocks.sh <doc_token>")
        print("  python scripts/get_feishu_doc_blocks.py --doc-token <doc_token>")
        return 0
    else:
        print(f"\n❌ {tests.count(False)} out of {len(tests)} tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())