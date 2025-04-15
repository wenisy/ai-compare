import sys
import math
import random
import pygame

# 可调参数
GRAVITY = 0.25  # 重力强度
FRICTION = 0.99  # 摩擦系数
HEXAGON_SIZES = [80, 140, 200, 260, 320]  # 每层六边形半径
ROTATION_SPEEDS = [0.5, -0.7, 1.1, -0.9, 0.6]  # 每层六边形旋转速度
BALL_COLORS = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255)]
BALL_RADIUS = 12

WIDTH, HEIGHT = 700, 700
CENTER = (WIDTH//2, HEIGHT//2)
FPS = 60

class Ball:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2,2)
        self.vy = random.uniform(-2,2)
        self.color = color
        self.radius = BALL_RADIUS
        self.omega = 0  # 角动量

    def update(self):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy
        self.vx *= FRICTION
        self.vy *= FRICTION
        self.omega *= FRICTION

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Hexagon:
    def __init__(self, radius, speed, missing_wall=None):
        self.radius = radius
        self.angle = 0
        self.speed = speed
        self.missing_wall = missing_wall if missing_wall is not None else random.randint(0,5)

    def update(self):
        self.angle += self.speed

    def get_walls(self):
        points = []
        for i in range(6):
            theta = math.radians(self.angle + i*60)
            x = CENTER[0] + self.radius * math.cos(theta)
            y = CENTER[1] + self.radius * math.sin(theta)
            points.append((x, y))
        walls = []
        for i in range(6):
            if i == self.missing_wall:
                walls.append(None)
            else:
                walls.append((points[i], points[(i+1)%6]))
        return walls

    def draw(self, screen):
        points = []
        for i in range(6):
            theta = math.radians(self.angle + i*60)
            x = CENTER[0] + self.radius * math.cos(theta)
            y = CENTER[1] + self.radius * math.sin(theta)
            points.append((x, y))
        for i in range(6):
            if i != self.missing_wall:
                pygame.draw.line(screen, (200,200,200), points[i], points[(i+1)%6], 3)

# 碰撞检测: 球与墙壁

def reflect_ball(ball, wall):
    (x1, y1), (x2, y2) = wall
    dx, dy = x2-x1, y2-y1
    length = math.hypot(dx, dy)
    nx, ny = dy/length, -dx/length  # 法向量
    # 球到直线距离
    px, py = ball.x, ball.y
    t = ((px-x1)*dx + (py-y1)*dy) / (length*length)
    t = max(0, min(1, t))
    closest_x = x1 + t*dx
    closest_y = y1 + t*dy
    dist = math.hypot(px-closest_x, py-closest_y)
    if dist < ball.radius:
        # 反射
        v_dot_n = ball.vx*nx + ball.vy*ny
        ball.vx -= 2*v_dot_n*nx
        ball.vy -= 2*v_dot_n*ny
        # 增加角动量
        ball.omega += v_dot_n*0.1
        # 推开球
        overlap = ball.radius - dist + 1
        ball.x += nx*overlap
        ball.y += ny*overlap

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # 创建嵌套六边形
    hexagons = []
    for i in range(len(HEXAGON_SIZES)):
        missing = None if i==0 else random.randint(0,5)
        hexagons.append(Hexagon(HEXAGON_SIZES[i], ROTATION_SPEEDS[i], missing))

    # 创建球
    balls = []
    for i in range(5):
        angle = random.uniform(0, 2*math.pi)
        r = HEXAGON_SIZES[0] * 0.5 * random.uniform(0.2, 0.8)
        x = CENTER[0] + r * math.cos(angle)
        y = CENTER[1] + r * math.sin(angle)
        balls.append(Ball(x, y, BALL_COLORS[i]))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((20, 20, 30))

        # 更新六边形
        for hexagon in hexagons:
            hexagon.update()
            hexagon.draw(screen)

        # 球物理与碰撞
        for ball in balls:
            ball.update()
            # 检查每层六边形的墙壁
            for i, hexagon in enumerate(hexagons):
                for wall in hexagon.get_walls():
                    if wall is not None:
                        reflect_ball(ball, wall)
            ball.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()
