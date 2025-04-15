import pygame, math, random, sys

# 提示：请在虚拟环境(venv)或其他隔离环境中运行此脚本

# 可调参数
WIDTH, HEIGHT = 800, 600
NUM_HEX = 3
HEX_SIZE = [200, 130, 60]
BALL_COUNT = 5
GRAVITY = 0.2
FRICTION = 0.99
ROTATION_SPEEDS = [0.5, -0.7, 1.2]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 创建球
balls = []
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255)]
for i in range(BALL_COUNT):
    balls.append({
        "pos": [WIDTH/2, HEIGHT/2], # 坐标初始在最内层
        "vel": [random.uniform(-2, 2), random.uniform(-2, 2)],
        "color": colors[i % len(colors)]
    })

# 创建六边形数据：每个六边形含尺寸、旋转角度、旋转速度、缺失边
hexagons = []
for i in range(NUM_HEX):
    missing_edge = random.randint(0,5) if i < NUM_HEX - 1 else -1
    hexagons.append({
        "size": HEX_SIZE[i],
        "angle": 0,
        "speed": ROTATION_SPEEDS[i % len(ROTATION_SPEEDS)],
        "missing_edge": missing_edge
    })

def draw_hexagon(center, size, angle, missing_edge):
    points = []
    for i in range(6):
        if i == missing_edge: # 跳过缺失边
            continue
        a = math.radians(60*i + angle)
        x = center[0] + size * math.cos(a)
        y = center[1] + size * math.sin(a)
        points.append((x, y))
    if len(points) > 1:
        pygame.draw.lines(screen, (200,200,200), True, points, 2)

def update_ball(ball):
    # 应用重力
    ball["vel"][1] += GRAVITY
    # 速度衰减
    ball["vel"][0] *= FRICTION
    ball["vel"][1] *= FRICTION

    # 更新位置
    ball["pos"][0] += ball["vel"][0]
    ball["pos"][1] += ball["vel"][1]

    # 边界简单处理
    if ball["pos"][0] < 0 or ball["pos"][0] > WIDTH:
        ball["vel"][0] *= -1
    if ball["pos"][1] < 0 or ball["pos"][1] > HEIGHT:
        ball["vel"][1] *= -1

def check_collision(ball, hx):
    # 计算六边形所有边所在的线段，用向量法检测球是否与某条线段相交
    # 若碰撞则反弹，可根据需要做更加复杂的碰撞处理
    pass

running = True
while running:
    screen.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    for hx in hexagons:
        hx["angle"] += hx["speed"]
        draw_hexagon((WIDTH/2, HEIGHT/2), hx["size"], hx["angle"], hx["missing_edge"])

    for b in balls:
        update_ball(b)
        for hx in hexagons:
            check_collision(b, hx)
        pygame.draw.circle(screen, b["color"], (int(b["pos"][0]), int(b["pos"][1])), 10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()