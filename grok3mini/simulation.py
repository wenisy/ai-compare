import pygame
import sys
import math
import random

# 初始化 Pygame
pygame.init()

# 设置参数
WIDTH, HEIGHT = 800, 600  # 窗口大小
FPS = 60  # 帧率
GRAVITY = 0.5  # 重力强度（可调整）
FRICTION = 0.99  # 摩擦系数（可调整）
HEX_SIZES = [200, 150, 100, 50, 25]  # 六边形大小，从外到内（可调整）
ROTATION_SPEEDS = [0.01, 0.02, 0.03, 0.04, 0.05]  # 每个六边形的旋转速度（可调整）

# 颜色
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]  # 五种不同颜色的球

class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = random.uniform(-5, 5)  # 初始速度
        self.vy = random.uniform(-5, 5)

    def update(self):
        self.vy += GRAVITY  # 应用重力
        self.x += self.vx
        self.vy *= FRICTION  # 应用摩擦
        self.vx *= FRICTION

        # 边界检查（简单实现，实际中需处理六边形碰撞）
        if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
            self.vx *= -1  # 反弹
        if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
            self.vy *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Hexagon:
    def __init__(self, center_x, center_y, size, rotation_speed, missing_wall=None):
        self.center_x = center_x
        self.center_y = center_y
        self.size = size
        self.rotation_speed = rotation_speed
        self.angle = 0
        self.missing_wall = missing_wall  # 随机缺失一面

    def update(self):
        self.angle += self.rotation_speed

    def draw(self, screen):
        points = []
        for i in range(6):
            angle_deg = 60 * i + self.angle
            angle_rad = math.radians(angle_deg)
            x = self.center_x + self.size * math.cos(angle_rad)
            y = self.center_y + self.size * math.sin(angle_rad)
            points.append((x, y))
        
        if self.missing_wall is not None:
            # 移除缺失的一面（简单处理：不绘制那条线）
            points_missing = points.copy()
            if self.missing_wall == 0:
                points_missing = points_missing[1:] + [points_missing[0]]  # 示例，实际需调整
            pygame.draw.polygon(screen, (255, 255, 255), points_missing, 1)  # 绘制多边形但缺失一面
        else:
            pygame.draw.polygon(screen, (255, 255, 255), points, 1)

# 设置窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Balls in Rotating Hexagons")
clock = pygame.time.Clock()

# 创建球
balls = [Ball(WIDTH//2, HEIGHT//2, 10, COLORS[i]) for i in range(5)]  # 初始在中心

# 创建六边形，从外到内
hexagons = []
center_x, center_y = WIDTH//2, HEIGHT//2
for size, speed in zip(HEX_SIZES, ROTATION_SPEEDS):
    missing = random.choice([0, 1, 2, 3, 4, 5]) if size != HEX_SIZES[-1] else None  # 最外层无缺失
    hexagons.append(Hexagon(center_x, center_y, size, speed, missing))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for hexagon in hexagons:
        hexagon.update()

    for ball in balls:
        ball.update()
        # 这里应添加碰撞检测，但简化了

    screen.fill((0, 0, 0))  # 黑色背景

    for hexagon in hexagons:
        hexagon.draw(screen)

    for ball in balls:
        ball.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()