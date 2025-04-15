import pygame
import math
import random
from pygame.locals import *

# 初始化pygame
pygame.init()

# 设置窗口大小和标题
WIDTH = 800
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Balls in Rotating Hexagons")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# 可调整参数
GRAVITY = 0.2  # 重力强度
FRICTION = 0.98  # 摩擦系数
HEXAGON_SIZES = [100, 200, 300, 400]  # 六边形大小（半径）
ROTATION_SPEEDS = [0.02, 0.015, 0.01, 0.005]  # 六边形旋转速度（弧度/帧）
BALL_RADIUS = 10
BALL_COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE]

# 小球类
class Ball:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.color = color

    def update(self):
        self.vy += GRAVITY
        self.vx *= FRICTION
        self.vy *= FRICTION
        self.x += self.vx
        self.y += self.vy

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), BALL_RADIUS)

# 六边形类
class Hexagon:
    def __init__(self, size, speed, missing_wall):
        self.size = size
        self.speed = speed
        self.angle = 0
        self.missing_wall = missing_wall  # 缺失的墙壁索引（0-5）

    def get_vertices(self, center_x, center_y):
        vertices = []
        for i in range(6):
            angle = self.angle + i * math.pi / 3
            x = center_x + self.size * math.cos(angle)
            y = center_y + self.size * math.sin(angle)
            vertices.append((x, y))
        return vertices

    def update(self):
        self.angle += self.speed

# 初始化小球（从最内层六边形开始）
balls = [Ball(WIDTH // 2 + random.uniform(-50, 50), HEIGHT // 2 + random.uniform(-50, 50), color) for color in BALL_COLORS]

# 初始化六边形（最外层没有缺失墙壁）
hexagons = []
for i in range(len(HEXAGON_SIZES)):
    missing_wall = random.randint(0, 5) if i < len(HEXAGON_SIZES) - 1 else -1
    hexagons.append(Hexagon(HEXAGON_SIZES[i], ROTATION_SPEEDS[i], missing_wall))

# 碰撞检测与响应
def check_collision(ball, hexagon, center_x, center_y):
    vertices = hexagon.get_vertices(center_x, center_y)
    for i in range(6):
        if i == hexagon.missing_wall:
            continue
        j = (i + 1) % 6
        if j == hexagon.missing_wall:
            continue
        x1, y1 = vertices[i]
        x2, y2 = vertices[j]
        if line_circle_collision(ball.x, ball.y, BALL_RADIUS, x1, y1, x2, y2):
            # 计算墙壁法线
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx * dx + dy * dy)
            nx = -dy / length
            ny = dx / length
            # 考虑旋转速度的影响
            wall_speed_x = -hexagon.speed * dy
            wall_speed_y = hexagon.speed * dx
            # 计算相对速度
            rel_vx = ball.vx - wall_speed_x
            rel_vy = ball.vy - wall_speed_y
            dot = rel_vx * nx + rel_vy * ny
            if dot < 0:  # 确保小球从外部接近墙壁
                ball.vx -= 2 * dot * nx
                ball.vy -= 2 * dot * ny
                ball.vx += wall_speed_x
                ball.vy += wall_speed_y
                ball.vx *= 0.9  # 碰撞后略微减速
                ball.vy *= 0.9

def line_circle_collision(cx, cy, radius, x1, y1, x2, y2):
    # 计算线段长度平方
    length2 = (x2 - x1) ** 2 + (y2 - y1) ** 2
    if length2 == 0:
        return math.hypot(cx - x1, cy - y1) <= radius
    # 计算投影
    t = max(0, min(1, ((cx - x1) * (x2 - x1) + (cy - y1) * (y2 - y1)) / length2))
    projection_x = x1 + t * (x2 - x1)
    projection_y = y1 + t * (y2 - y1)
    return math.hypot(cx - projection_x, cy - projection_y) <= radius

# 主循环
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

    # 更新六边形
    for hexagon in hexagons:
        hexagon.update()

    # 更新小球
    for ball in balls:
        ball.update()
        # 检查与每个六边形的碰撞
        for hexagon in hexagons:
            check_collision(ball, hexagon, WIDTH // 2, HEIGHT // 2)

    # 绘制
    screen.fill(BLACK)
    # 绘制六边形
    for hexagon in hexagons:
        vertices = hexagon.get_vertices(WIDTH // 2, HEIGHT // 2)
        for i in range(6):
            if i != hexagon.missing_wall:
                j = (i + 1) % 6
                if j != hexagon.missing_wall:
                    pygame.draw.line(screen, WHITE, vertices[i], vertices[j], 2)
    # 绘制小球
    for ball in balls:
        ball.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()