#!/bin/bash

# 飞书文档读取脚本 - 严格配置文件版本
# 用法: ./read_doc.sh <doc_token> [doc|sheet|docx]

set -euo pipefail

# 配置文件路径（严格从这里读取）
CONFIG_FILE="./reference/feishu_config.json"

# 验证配置文件存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在: $CONFIG_FILE" >&2
    echo "请创建配置文件，格式如下:" >&2
    echo '{' >&2
    echo '  "app_id": "your_app_id_here",' >&2
    echo '  "app_secret": "your_app_secret_here"' >&2
    echo '}' >&2
    exit 1
fi

# 从配置文件读取凭据
APP_ID=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['app_id'])" 2>/dev/null || echo "")
APP_SECRET=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['app_secret'])" 2>/dev/null || echo "")

# 验证配置
if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
    echo "错误: 配置文件 $CONFIG_FILE 中缺少 app_id 或 app_secret" >&2
    exit 1
fi

# 参数验证
if [ $# -lt 1 ]; then
    echo "用法: $0 <document_token> [doc|sheet|docx]" >&2
    echo "示例:" >&2
    echo "  $0 docx_xxxxxxxxxxxxxxx     # 读取新格式文档 (docx)" >&2
    echo "  $0 doc_xxxxxxxxxxxxxxx      # 读取旧格式文档 (doc)" >&2
    echo "  $0 sheet_xxxxxxxxxxxxxxx    # 读取表格 (sheet)" >&2
    exit 1
fi

DOC_TOKEN=$1
DOC_TYPE=${2:-auto}

# 自动检测文档类型
if [ "$DOC_TYPE" = "auto" ]; then
    if [[ "$DOC_TOKEN" == docx_* ]]; then
        DOC_TYPE="docx"
    elif [[ "$DOC_TOKEN" == doc_* ]]; then
        DOC_TYPE="doc"
    elif [[ "$DOC_TOKEN" == sheet_* ]]; then
        DOC_TYPE="sheet"
    else
        echo "警告: 无法自动检测文档类型，使用默认类型 'docx'" >&2
        DOC_TYPE="docx"
    fi
fi

echo "正在读取飞书文档: $DOC_TOKEN" >&2
echo "文档类型: $DOC_TYPE" >&2

# 执行 Python 脚本（只传递文档 token，让 Python 脚本自动处理类型）
python3 scripts/read_feishu_doc.py "$DOC_TOKEN"