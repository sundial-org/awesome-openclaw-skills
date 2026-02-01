#!/usr/bin/env python3
"""
飞书文档读取技能打包脚本
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path

def validate_skill(skill_path):
    """验证技能目录结构"""
    skill_dir = Path(skill_path)
    
    # 检查必需文件
    required_files = ["SKILL.md"]
    for file in required_files:
        if not (skill_dir / file).exists():
            raise ValueError(f"Missing required file: {file}")
    
    # 检查SKILL.md格式
    with open(skill_dir / "SKILL.md", "r", encoding="utf-8") as f:
        content = f.read()
        if not content.startswith("---"):
            raise ValueError("SKILL.md must start with YAML frontmatter")
    
    print("✓ Skill validation passed")

def package_skill(skill_path, output_dir=None):
    """打包技能为.skill文件"""
    skill_dir = Path(skill_path)
    skill_name = skill_dir.name
    
    if output_dir is None:
        output_dir = skill_dir.parent
    else:
        output_dir = Path(output_dir)
    
    output_file = output_dir / f"{skill_name}.skill"
    
    # 验证技能
    validate_skill(skill_path)
    
    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = Path(root) / file
                # 计算相对路径
                rel_path = file_path.relative_to(skill_dir.parent)
                zipf.write(file_path, rel_path)
    
    print(f"✓ Skill packaged successfully: {output_file}")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        package_skill(skill_path, output_dir)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)