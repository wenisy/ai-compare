import pygame
import math
import random

# 初始化 Pygame
pygame.init()

# 屏幕尺寸
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bouncing Balls in Rotating Hexagons")

# 颜色
white = (255, 255, 255)
black = (0, 0, 0)
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

# 参数
gravity = 0.1
friction = 0.01
num_balls = 5
num_hexagons = 4
hexagon_size = 50
rotation_speeds = [0.5, -0.7, 0.9, -1.1]

# 球类
class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity_x = random.uniform(-2, 2)
        self.velocity_y = random.uniform(-2, 2)

    def move(self):
        self.velocity_y += gravity
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_x *= (1 - friction)
        self.velocity_y *= (1 - friction)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# 六边形类
class Hexagon:
    def __init__(self, x, y, size, rotation_speed, missing_wall=None):
        self.x = x
        self.y = y
        self.size = size
        self.rotation_speed = rotation_speed
        self.angle = 0
        self.missing_wall = missing_wall

    def rotate(self):
        self.angle += self.rotation_speed

    def draw(self, screen):
        points = []
        for i in range(6):
            if self.missing_wall is not None and i == self.missing_wall:
                continue
            angle_rad = math.radians(60 * i + self.angle)
            x = self.x + self.size * math.cos(angle_rad)
            y = self.y + self.size * math.sin(angle_rad)
            points.append((x, y))

        if len(points) > 1:
            pygame.draw.polygon(screen, white, points, 1)

# 创建球
balls = []
for _ in range(num_balls):
    balls.append(Ball(screen_width / 2, screen_height / 2, 10, random.choice(colors)))

# 创建六边形
hexagons = []
for i in range(num_hexagons):
    size = hexagon_size * (num_hexagons - i)
    missing_wall = random.randint(0, 5) if i > 0 else None
    hexagons.append(Hexagon(screen_width / 2, screen_height / 2, size, rotation_speeds[i], missing_wall))

# 游戏循环
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 移动球
    for ball in balls:
        ball.move()

        # 碰撞检测 (简化)
        for hexagon in hexagons:
            distance = math.sqrt((ball.x - hexagon.x) ** 2 + (ball.y - hexagon.y) ** 2)
            if distance > hexagon.size:
                continue

            # 非常简化的碰撞反应
            ball.velocity_x *= -0.5
            ball.velocity_y *= -0.5

            # 边界检测
            if ball.x < 0 or ball.x > screen_width:
                ball.velocity_x *= -1
            if ball.y < 0 or ball.y > screen_height:
                ball.velocity_y *= -1

    # 旋转六边形
    for hexagon in hexagons:
        hexagon.rotate()

    # 绘制
    screen.fill(black)
    for hexagon in hexagons:
        hexagon.draw(screen)
    for ball in balls:
        ball.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()