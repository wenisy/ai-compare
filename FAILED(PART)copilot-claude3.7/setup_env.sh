#!/bin/bash
# 此脚本创建并设置Python虚拟环境，实现完全的环境隔离

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 显示环境信息
echo "环境设置完成！"
echo "激活的Python解释器: $(which python)"
echo "已安装的包:"
pip list

# 使用说明
echo ""
echo "使用方法:"
echo "1. 激活环境: source venv/bin/activate"
echo "2. 运行模拟: python bouncing_balls.py"
echo "3. 退出环境: deactivate"