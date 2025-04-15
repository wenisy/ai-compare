import pygame
import sys
import math
import random

# 可调参数
GRAVITY = 0.25
FRICTION = 0.995
HEXAGON_COUNT = 4
HEXAGON_SIZES = [80, 140, 200, 260]
ROTATION_SPEEDS = [0.01, -0.013, 0.018, -0.022]
BALL_COLORS = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255)]
BALL_RADIUS = 12

WIDTH, HEIGHT = 600, 600
CENTER = (WIDTH//2, HEIGHT//2)

class Ball:
    def __init__(self, color):
        angle = random.uniform(0, 2*math.pi)
        r = HEXAGON_SIZES[0] * 0.5 * random.uniform(0.2, 0.8)
        self.x = CENTER[0] + r * math.cos(angle)
        self.y = CENTER[1] + r * math.sin(angle)
        self.vx = random.uniform(-2,2)
        self.vy = random.uniform(-2,2)
        self.color = color
        self.radius = BALL_RADIUS

    def update(self):
        self.vy += GRAVITY
        self.vx *= FRICTION
        self.vy *= FRICTION
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def hexagon_points(center, radius, angle_offset=0):
    return [
        (
            center[0] + radius * math.cos(angle_offset + math.pi/3 * i),
            center[1] + radius * math.sin(angle_offset + math.pi/3 * i)
        )
        for i in range(6)
    ]

def reflect(vx, vy, nx, ny):
    dot = vx*nx + vy*ny
    return vx - 2*dot*nx, vy - 2*dot*ny

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # 随机每层缺失一边
    missing_walls = [random.randint(0,5) for _ in range(HEXAGON_COUNT-1)]
    angles = [0 for _ in range(HEXAGON_COUNT)]
    balls = [Ball(BALL_COLORS[i]) for i in range(5)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((18,18,18))

        # 画六边形
        hexes = []
        for i in range(HEXAGON_COUNT):
            angles[i] += ROTATION_SPEEDS[i]
            pts = hexagon_points(CENTER, HEXAGON_SIZES[i], angles[i])
            hexes.append(pts)
            # 画墙
            for j in range(6):
                if i < HEXAGON_COUNT-1 and j == missing_walls[i]:
                    continue
                pygame.draw.line(screen, (180,180,180), pts[j], pts[(j+1)%6], 2)

        # 球物理与碰撞
        for ball in balls:
            ball.update()
            # 从内到外检测碰撞
            for i in range(HEXAGON_COUNT):
                pts = hexes[i]
                # 缺失墙不检测
                for j in range(6):
                    if i < HEXAGON_COUNT-1 and j == missing_walls[i]:
                        continue
                    a, b = pts[j], pts[(j+1)%6]
                    # 点到线段距离
                    dx, dy = b[0]-a[0], b[1]-a[1]
                    length = math.hypot(dx, dy)
                    if length == 0: continue
                    nx, ny = dy/length, -dx/length  # 外法线
                    px, py = ball.x - a[0], ball.y - a[1]
                    proj = px*nx + py*ny
                    # 只检测外侧
                    if proj > 0: continue
                    # 球到墙距离
                    dist = abs((dx)*(a[1]-ball.y)-(a[0]-ball.x)*(dy))/length
                    if dist < ball.radius:
                        # 反射
                        ball.x += nx * (ball.radius - dist)
                        ball.y += ny * (ball.radius - dist)
                        ball.vx, ball.vy = reflect(ball.vx, ball.vy, nx, ny)
                        # 增加角动量效果
                        tangent = (-ny, nx)
                        tangent_speed = ball.vx*tangent[0] + ball.vy*tangent[1]
                        ball.vx += tangent[0]*0.05*tangent_speed
                        ball.vy += tangent[1]*0.05*tangent_speed

            ball.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()