#!/bin/bash
# ETF投资助理 - Clawdbot Skill
# 功能：ETF查询、行情、筛选、对比、定投计算

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 常用ETF列表
ETF_LIST="510300:沪深300ETF
510500:中证500ETF
159915:创业板ETF
159941:纳指ETF
513100:恒生ETF
510880:红利ETF
159919:科创50ETF
159997:芯片ETF
159995:新能源车ETF
512880:光伏ETF
512760:券商ETF
512170:医疗ETF
159845:中证1000ETF
511880:中证消费ETF"

show_help() {
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║      ETF投资助理 - Clawdbot Skill       ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "用法: $0 <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  list              显示常用ETF列表"
    echo "  price <代码>      查询ETF实时行情"
    echo "  hot               显示热门ETF"
    echo "  search <关键词>   搜索ETF"
    echo "  compare <代码1> <代码2>  对比两只ETF"
    echo "  calc <代码> <金额> <年限>  定投计算器"
    echo "  summary           ETF投资摘要"
    echo "  help              显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 list"
    echo "  $0 price 510300"
    echo "  $0 hot"
    echo "  $0 compare 510300 159915"
    echo "  $0 calc 510300 1000 10"
}

get_etf_name() {
    local code=$1
    echo "$ETF_LIST" | grep "^${code}:" | cut -d: -f2 | sed 's/^/未知ETF/g'
}

# 显示ETF列表
cmd_list() {
    echo -e "${GREEN}📊 常用ETF列表${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━"
    printf "%-10s %-20s\n" "代码" "名称"
    echo "━━━━━━━━━━━━━━━━━━━━"
    echo "$ETF_LIST" | sort
    echo "━━━━━━━━━━━━━━━━━━━━"
}

# 查询ETF行情 (使用Yahoo Finance API)
cmd_price() {
    local code=$1
    if [ -z "$code" ]; then
        echo -e "${RED}❌ 请输入ETF代码${NC}"
        return 1
    fi
    
    local name=$(get_etf_name "$code")
    echo -e "${GREEN}📈 $name ($code) 实时行情${NC}"
    echo ""
    
    # 使用curl获取数据
    local response=$(curl -s "https://query1.finance.yahoo.com/v8/finance/chart/${code}.SS" 2>/dev/null | head -100)
    
    if echo "$response" | grep -q "timestamp"; then
        # 提取价格数据
        local current=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    result = data.get('chart', {}).get('result', [{}])[0]
    meta = result.get('meta', {})
    print(meta.get('regularMarketPrice', 'N/A'))
except: print('N/A')
" 2>/dev/null)
        
        local prev_close=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    result = data.get('chart', {}).get('result', [{}])[0]
    meta = result.get('meta', {})
    print(meta.get('previousClose', 'N/A'))
except: print('N/A')
" 2>/dev/null)
        
        local change=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    result = data.get('chart', {}).get('result', [{}])[0]
    meta = result.get('meta', {})
    diff = float(meta.get('regularMarketPrice', 0)) - float(meta.get('previousClose', 0))
    pct = diff / float(meta.get('previousClose', 1)) * 100
    print(f'{diff:+.4f} ({pct:+.2f}%)')
except: print('N/A')
" 2>/dev/null)
        
        echo -e "当前价格: ${GREEN}$current${NC}"
        echo -e "昨收: $prev_close"
        echo -e "涨跌: $change"
        
        # 获取涨跌幅颜色
        if [[ "$change" == +* ]]; then
            echo -e "${GREEN}📈 上涨${NC}"
        else
            echo -e "${RED}📉 下跌${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  暂时无法获取行情数据${NC}"
        echo "可能原因: 网络问题或代码不存在"
    fi
}

# 热门ETF
cmd_hot() {
    echo -e "${GREEN}🔥 热门ETF${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━"
    echo "1. 沪深300ETF (510300) - 蓝筹白马"
    echo "2. 科创50ETF (159919) - 科技创新"
    echo "3. 纳指ETF (159941) - 美股科技"
    echo "4. 恒生ETF (513100) - 港股核心"
    echo "5. 中证500ETF (510500) - 中盘成长"
    echo "6. 创业板ETF (159915) - 新兴产业"
    echo "7. 芯片ETF (159997) - 半导体"
    echo "8. 新能源车ETF (159995) - 新能源"
    echo "━━━━━━━━━━━━━━━━━━━━"
}

# 搜索ETF
cmd_search() {
    local keyword=$1
    if [ -z "$keyword" ]; then
        echo -e "${RED}❌ 请输入搜索关键词${NC}"
        return 1
    fi
    
    echo -e "${GREEN}🔍 搜索: $keyword${NC}"
    echo ""
    
    # 在ETF列表中搜索
    local results=$(echo "$ETF_LIST" | grep -i "$keyword")
    
    if [ -z "$results" ]; then
        echo "未找到相关ETF"
    else
        local count=$(echo "$results" | wc -l)
        echo "找到 $count 个结果:"
        echo "━━━━━━━━━━━━━━━━━━━━"
        echo "$results"
    fi
}

# ETF对比
cmd_compare() {
    local code1=$1
    local code2=$2
    
    if [ -z "$code1" ] || [ -z "$code2" ]; then
        echo -e "${RED}❌ 请输入两个ETF代码${NC}"
        echo "示例: $0 compare 510300 159915"
        return 1
    fi
    
    local name1=$(get_etf_name "$code1")
    local name2=$(get_etf_name "$code2")
    
    echo -e "${GREEN}📊 ETF对比分析${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━"
    echo -e "$code1 $name1  VS  $code2 $name2"
    echo "━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # 获取两只ETF的行情
    local price1=$(curl -s "https://query1.finance.yahoo.com/v8/finance/chart/${code1}.SS" 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    result = data.get('chart', {}).get('result', [{}])[0]
    print(result.get('meta', {}).get('regularMarketPrice', 'N/A'))
except: print('N/A')
" 2>/dev/null)
    
    local price2=$(curl -s "https://query1.finance.yahoo.com/v8/finance/chart/${code2}.SS" 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    result = data.get('chart', {}).get('result', [{}])[0]
    print(result.get('meta', {}).get('regularMarketPrice', 'N/A'))
except: print('N/A')
" 2>/dev/null)
    
    echo -e "当前价格:"
    echo "  $code1: $price1"
    echo "  $code2: $price2"
    echo ""
    echo "注: 完整对比需要更多历史数据"
}

# 定投计算器
cmd_calc() {
    local code=$1
    local amount=$2
    local years=$3
    
    if [ -z "$code" ] || [ -z "$amount" ] || [ -z "$years" ]; then
        echo -e "${RED}❌ 参数不全${NC}"
        echo "示例: $0 calc 510300 1000 10"
        echo "含义: 每月定投1000元，定投10年"
        return 1
    fi
    
    local name=$(get_etf_name "$code")
    
    echo -e "${GREEN}📈 定投计算器${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━"
    echo "ETF: $name ($code)"
    echo "月定投: ¥$amount"
    echo "定投年限: $years 年"
    echo "━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # 简化计算 (假设年化收益率8%)
    local months=$((years * 12))
    local annual_return=0.08
    local monthly_return=$(echo "scale=6; $annual_return / 12" | bc)
    
    # 使用复利公式计算
    local future_value=$(echo "scale=2; $amount * ((1 + $monthly_return)^$months - 1) / $monthly_return" | bc)
    local total_invest=$((amount * months))
    
    echo "📊 估算收益 (假设年化8%):"
    echo "  总投入: ¥$total_invest"
    echo "  预计价值: ¥$future_value"
    echo "  收益: ¥$(echo "scale=2; $future_value - $total_invest" | bc)"
    echo ""
    echo "💡 提示: 实际收益取决于市场表现"
}

# ETF投资摘要
cmd_summary() {
    echo -e "${GREEN}💼 ETF投资摘要${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📌 主流ETF分类:"
    echo ""
    echo "【宽基指数】"
    echo "  510300 沪深300 - 蓝筹白马代表"
    echo "  159915 创业板 - 新兴产业"
    echo "  159919 科创50 - 科技创新"
    echo "  159941 纳指100 - 美股科技"
    echo ""
    echo "【行业主题】"
    echo "  159997 芯片ETF - 半导体"
    echo "  159995 新能源车 - 新能源"
    echo "  512170 医疗ETF - 医药医疗"
    echo "  512880 光伏ETF - 光伏产业"
    echo ""
    echo "【港股/海外】"
    echo "  513100 恒生ETF - 港股核心"
    echo "  513050 中概互联 - 互联网"
    echo ""
    echo "【Smart Beta】"
    echo "  510880 红利ETF - 高股息"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━"
}

# 主逻辑
case "$1" in
    list)
        cmd_list
        ;;
    price)
        cmd_price "$2"
        ;;
    hot)
        cmd_hot
        ;;
    search)
        cmd_search "$2"
        ;;
    compare)
        cmd_compare "$2" "$3"
        ;;
    calc)
        cmd_calc "$2" "$3" "$4"
        ;;
    summary)
        cmd_summary
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac
