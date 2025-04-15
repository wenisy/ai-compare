#!/bin/bash

# 设置错误处理
set -e

# 显示彩色文本
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# 确保我们在脚本所在的目录中
cd "$(dirname "$0")"
echo -e "${GREEN}当前工作目录: $(pwd)${NC}"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到Python3。请安装Python 3.6+后再试。${NC}"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
source venv/bin/activate

# 安装依赖
echo -e "${YELLOW}安装依赖...${NC}"
pip install -r requirements.txt

# 运行模拟器
echo -e "${GREEN}启动弹球模拟器...${NC}"
echo -e "${YELLOW}按ESC键退出模拟器${NC}"
python bouncing_balls.py

# 退出虚拟环境
deactivate

echo -e "${GREEN}模拟器已关闭${NC}"
