#!/bin/bash

# 蓝牙设备监控脚本 / Bluetooth Device Monitor Script
# 用法: bluetooth-monitor <command> [args]
# Usage: bluetooth-monitor <command> [args]

set -e

# 颜色输出 / Color Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 检查blueutil是否安装 / Check blueutil installation
check_blueutil() {
    if ! command -v blueutil &> /dev/null; then
        echo -e "${RED}错误: blueutil 未安装${NC}"
        echo "请运行: brew install blueutil"
        echo "Run: brew install blueutil"
        exit 1
    fi
}

# 格式化设备地址 / Format device address
format_address() {
    echo "$1" | tr '[:lower:]' '[:upper:]'
}

# 获取蓝牙电量 / Get Bluetooth battery level
get_battery_level() {
    local name="$1"
    local battery=$(/usr/sbin/system_profiler SPBluetoothDataType 2>/dev/null | \
        grep -A10 "$name" | grep "Battery Level" | sed 's/.*: //' | tr -d '%')
    if [ -n "$battery" ]; then
        echo "$battery"
    else
        echo "N/A"
    fi
}

# 获取设备类型 / Get device type
get_device_type() {
    local name="$1"
    local device_type=$(/usr/sbin/system_profiler SPBluetoothDataType 2>/dev/null | \
        grep -A10 "$name" | grep "Minor Type" | sed 's/.*: //')
    if [ -n "$device_type" ]; then
        echo "$device_type"
    else
        echo "Unknown"
    fi
}

# 显示电量进度条 / Display battery progress bar
show_battery_bar() {
    local level="$1"
    local name="$2"
    
    if [ "$level" == "N/A" ]; then
        echo -e "   🔋 电量: ${YELLOW}不可用${NC}"
        return
    fi
    
    # 根据电量选择颜色
    local color="$GREEN"
    if [ "$level" -lt 30 ]; then
        color="$RED"
    elif [ "$level" -lt 60 ]; then
        color="$YELLOW"
    fi
    
    # 绘制进度条
    local bar=""
    local blocks=10
    local filled=$((level * blocks / 100))
    
    for ((i=0; i<filled; i++)); do
        bar="${bar}█"
    done
    for ((i=filled; i<blocks; i++)); do
        bar="${bar}░"
    done
    
    echo -e "   🔋 电量: ${color}${level}%${NC} ${bar}"
}

# 显示已连接设备 / Show connected devices
cmd_connected() {
    check_blueutil
    
    echo -e "${BLUE}📱 已连接的蓝牙设备 / Connected Bluetooth Devices:${NC}"
    echo "================================"
    
    devices=$(blueutil --connected 2>/dev/null)
    
    if [ -z "$devices" ]; then
        echo -e "${YELLOW}暂无已连接的蓝牙设备${NC}"
        echo "No connected Bluetooth devices"
        exit 0
    fi
    
    echo "$devices" | while IFS= read -r line; do
        if [[ $line == address:* ]]; then
            addr=$(echo "$line" | sed 's/.*address: \([^,]*\),.*/\1/')
            addr=$(format_address "$addr")
            name=$(echo "$line" | sed 's/.*name: "\([^"]*\)".*/\1/')
            
            echo -e "🔗 ${GREEN}$name${NC}"
            echo "   地址 / Address: $addr"
            
            # 获取电量 / Get battery level
            battery=$(get_battery_level "$name")
            device_type=$(get_device_type "$name")
            echo "   类型 / Type: $device_type"
            show_battery_bar "$battery" "$name"
            echo ""
        fi
    done
}

# 显示已配对设备 / Show paired devices
cmd_paired() {
    check_blueutil
    
    echo -e "${BLUE}📋 已配对的蓝牙设备 / Paired Bluetooth Devices:${NC}"
    echo "================================"
    
    devices=$(blueutil --paired 2>/dev/null)
    
    if [ -z "$devices" ] || [[ "$devices" == "[]" ]]; then
        echo -e "${YELLOW}暂无已配对的蓝牙设备${NC}"
        echo "No paired Bluetooth devices"
        exit 0
    fi
    
    echo "$devices" | while IFS= read -r line; do
        if [[ $line == address:* ]]; then
            addr=$(echo "$line" | sed 's/.*address: \([^,]*\),.*/\1/')
            addr=$(format_address "$addr")
            name=$(echo "$line" | sed 's/.*name: "\([^"]*\)".*/\1/')
            connected=$(echo "$line" | grep -o 'connected' || echo "")
            
            if [ -n "$connected" ]; then
                echo -e "🔗 ${GREEN}$name${NC} (已连接 / Connected)"
                # 获取电量 / Get battery level
                battery=$(get_battery_level "$name")
                show_battery_bar "$battery" "$name"
            else
                echo -e "🔗 $name (未连接 / Disconnected)"
            fi
            echo "   地址 / Address: $addr"
            echo ""
        fi
    done
}

# 连接设备 / Connect device
cmd_connect() {
    local addr="$1"
    
    if [ -z "$addr" ]; then
        echo -e "${RED}用法: bluetooth-monitor connect <设备地址>${NC}"
        echo "Usage: bluetooth-monitor connect <device address>"
        echo "示例: bluetooth-monitor connect 08-65-18-B9-9C-B2"
        exit 1
    fi
    
    check_blueutil
    
    addr=$(format_address "$addr")
    echo -e "${BLUE}正在连接到设备 / Connecting to device: $addr${NC}"
    
    if blueutil --connect "$addr" 2>/dev/null; then
        echo -e "${GREEN}✅ 连接成功 / Connected successfully${NC}"
    else
        echo -e "${RED}❌ 连接失败 / Connection failed${NC}"
        exit 1
    fi
}

# 断开设备 / Disconnect device
cmd_disconnect() {
    local addr="$1"
    
    if [ -z "$addr" ]; then
        echo -e "${RED}用法: bluetooth-monitor disconnect <设备地址>${NC}"
        echo "Usage: bluetooth-monitor disconnect <device address>"
        echo "示例: bluetooth-monitor disconnect 08-65-18-B9-9C-B2"
        exit 1
    fi
    
    check_blueutil
    
    addr=$(format_address "$addr")
    echo -e "${BLUE}正在断开设备 / Disconnecting device: $addr${NC}"
    
    if blueutil --disconnect "$addr" 2>/dev/null; then
        echo -e "${GREEN}✅ 已断开 / Disconnected${NC}"
    else
        echo -e "${RED}❌ 操作失败 / Operation failed${NC}"
        exit 1
    fi
}

# 蓝牙电源状态 / Bluetooth power status
cmd_power() {
    check_blueutil
    
    local state="$1"
    
    if [ -z "$state" ]; then
        # 显示当前状态 / Show current status
        local power=$(blueutil --power)
        if [ "$power" == "1" ]; then
            echo -e "${GREEN}🔵 蓝牙已开启 / Bluetooth is ON${NC}"
        else
            echo -e "${RED}⚫ 蓝牙已关闭 / Bluetooth is OFF${NC}"
        fi
    else
        # 设置状态 / Set status
        if [[ "$state" == "on" || "$state" == "1" ]]; then
            echo -e "${BLUE}正在开启蓝牙... / Turning Bluetooth ON...${NC}"
            blueutil --power 1
            echo -e "${GREEN}✅ 蓝牙已开启 / Bluetooth is ON${NC}"
        elif [[ "$state" == "off" || "$state" == "0" ]]; then
            echo -e "${BLUE}正在关闭蓝牙... / Turning Bluetooth OFF...${NC}"
            blueutil --power 0
            echo -e "${YELLOW}⚠️ 蓝牙已关闭 / Bluetooth is OFF${NC}"
        else
            echo -e "${RED}用法: bluetooth-monitor power [on|off]${NC}"
            echo "Usage: bluetooth-monitor power [on|off]"
            exit 1
        fi
    fi
}

# 显示帮助 / Show help
cmd_help() {
    echo "蓝牙设备监控 v2.0.0 / Bluetooth Device Monitor"
    echo ""
    echo "用法: bluetooth-monitor <命令> [参数]"
    echo "Usage: bluetooth-monitor <command> [args]"
    echo ""
    echo "命令 Commands:"
    echo "  connected          查看已连接的蓝牙设备"
    echo "                     View connected Bluetooth devices"
    echo ""
    echo "  paired             查看已配对的蓝牙设备"
    echo "                     View paired Bluetooth devices"
    echo ""
    echo "  connect <地址>     连接到指定设备"
    echo "  connect <addr>     Connect to specified device"
    echo ""
    echo "  disconnect <地址>  断开指定设备"
    echo "  disconnect <addr>  Disconnect specified device"
    echo ""
    echo "  power [on|off]     查看/设置蓝牙电源状态"
    echo "  power [on|off]     View/set Bluetooth power status"
    echo ""
    echo "  help               显示此帮助信息"
    echo "                     Show this help message"
    echo ""
    echo "示例 / Examples:"
    echo "  bluetooth-monitor connected"
    echo "  bluetooth-monitor paired"
    echo "  bluetooth-monitor connect 08-65-18-B9-9C-B2"
    echo "  bluetooth-monitor power on"
}

# 主逻辑 / Main logic
main() {
    local command="${1:-}"
    shift || true
    
    case "$command" in
        connected|c)
            cmd_connected
            ;;
        paired|p)
            cmd_paired
            ;;
        connect|conn)
            cmd_connect "$@"
            ;;
        disconnect|disconn)
            cmd_disconnect "$@"
            ;;
        power|pw)
            cmd_power "$@"
            ;;
        help|--help|-h|"")
            cmd_help
            ;;
        *)
            echo -e "${RED}未知命令: $command${NC}"
            echo "Unknown command: $command"
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
