#!/bin/bash

# 确保我们在脚本所在的目录中
cd "$(dirname "$0")"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 运行测试脚本
echo "运行Pygame测试..."
python test_pygame.py

# 退出虚拟环境
deactivate
