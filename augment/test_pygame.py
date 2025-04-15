#!/usr/bin/env python3
"""
简单的Pygame测试脚本
用于验证Pygame是否正确安装和运行
"""

import pygame
import sys

# 初始化pygame
pygame.init()

# 打印pygame版本
print(f"Pygame版本: {pygame.version.ver}")
print("Pygame已成功初始化!")

# 创建一个小窗口
try:
    screen = pygame.display.set_mode((300, 200))
    pygame.display.set_caption("Pygame测试")
    print("成功创建窗口!")
    
    # 填充背景色
    screen.fill((0, 0, 0))
    pygame.display.flip()
    
    # 等待几秒钟
    pygame.time.wait(3000)
    
    # 退出
    pygame.quit()
    print("测试成功完成!")
    sys.exit(0)
except Exception as e:
    print(f"错误: {e}")
    pygame.quit()
    sys.exit(1)
