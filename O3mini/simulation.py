import sys
import math
import random
import pygame

# 可调参数
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.4         # 重力强度
FRICTION = 0.995      # 摩擦系数
NUM_BALLS = 5         # 小球数量
BALL_RADIUS = 8

NUM_HEX = 4           # 六边形数量（最外层完整，其余随机缺失一面）
HEX_BASE_SIZE = 250   # 最外层六边形半径
# 每层缩放比例（内层更小）
HEX_SCALE = 0.7

# 每个六边形的旋转速度（单位：度/帧）
HEX_ROT_SPEEDS = [0, 1.0, -1.5, 2.0]  # 外层为0（固定），内层各不相同

# 定义颜色
BG_COLOR = (30, 30, 30)
HEX_COLOR = (200, 200, 200)
BALL_COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255)
]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nested Rotating Hexagons with Bouncing Balls")
clock = pygame.time.Clock()

# 辅助函数：计算点到线段的距离及最近点
def line_point_distance(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    vx = bx - ax
    vy = by - ay
    mag = vx*vx + vy*vy
    if mag == 0:
        return math.hypot(px-ax, py-ay), a
    u = ((px-ax)*vx + (py-ay)*vy) / mag
    u = max(0, min(1, u))
    closest = (ax + u*vx, ay + u*vy)
    return math.hypot(px-closest[0], py-closest[1]), closest

# 六边形类
class Hexagon:
    def __init__(self, center, radius, rot_speed, missing_edge=None):
        self.center = center
        self.radius = radius
        self.angle = 0  # 当前旋转角度，单位度
        self.rot_speed = rot_speed
        self.missing_edge = missing_edge  # None 表示无缺失

    def update(self):
        self.angle = (self.angle + self.rot_speed) % 360

    def get_vertices(self):
        cx, cy = self.center
        vertices = []
        for i in range(6):
            theta = math.radians(self.angle + i * 60)
            x = cx + self.radius * math.cos(theta)
            y = cy + self.radius * math.sin(theta)
            vertices.append((x, y))
        return vertices

    def draw(self, surface):
        vertices = self.get_vertices()
        for i in range(6):
            if self.missing_edge is not None and i == self.missing_edge:
                continue
            start = vertices[i]
            end = vertices[(i+1)%6]
            pygame.draw.line(surface, HEX_COLOR, start, end, 2)

# 小球类
class Ball:
    def __init__(self, pos, vel, color, radius=BALL_RADIUS):
        self.pos = list(pos)
        self.vel = list(vel)
        self.color = color
        self.radius = radius

    def update(self):
        # 应用重力
        self.vel[1] += GRAVITY
        # 更新位置
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        # 应用摩擦
        self.vel[0] *= FRICTION
        self.vel[1] *= FRICTION

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)

    def collide_with_line(self, a, b):
        # 检测小球与线段 a->b 的碰撞
        dist, closest = line_point_distance(self.pos, a, b)
        if dist < self.radius:
            # 计算法向量
            ax, ay = a
            bx, by = b
            lx = bx - ax
            ly = by - ay
            # 法向量（垂直于线段）
            nx = -ly
            ny = lx
            norm = math.hypot(nx, ny)
            if norm == 0:
                return
            nx /= norm
            ny /= norm

            # 碰撞反弹: 如果小球正朝向墙体运动，则反弹
            dot = self.vel[0]*nx + self.vel[1]*ny
            if dot < 0:
                self.vel[0] -= 2 * dot * nx
                self.vel[1] -= 2 * dot * ny
                # 将小球移动到碰撞边缘以防穿透
                overlap = self.radius - dist
                self.pos[0] += nx * overlap
                self.pos[1] += ny * overlap

# 创建多个六边形（最外层无缺失，其余每个随机缺失一个边）
def create_hexagons():
    center = (WIDTH/2, HEIGHT/2)
    hexagons = []
    radius = HEX_BASE_SIZE
    for i in range(NUM_HEX):
        rot_speed = HEX_ROT_SPEEDS[i] if i < len(HEX_ROT_SPEEDS) else 1.0
        # 外层六边形完整，其它随机缺失一面
        missing_edge = None if i == 0 else random.randint(0, 5)
        hexagons.append(Hexagon(center, radius, rot_speed, missing_edge))
        radius *= HEX_SCALE
    return hexagons

# 创建小球，初始位置在最内层六边形内（随机）
def create_balls(inner_hex):
    balls = []
    center = inner_hex.center
    for i in range(NUM_BALLS):
        # 随机在最内层六边形内部生成点（简单使用圆形区域近似内嵌六边形）
        angle = random.uniform(0, 2*math.pi)
        r = random.uniform(0, inner_hex.radius * 0.8)
        pos = (center[0] + r * math.cos(angle), center[1] + r * math.sin(angle))
        vel = (random.uniform(-2,2), random.uniform(-2,2))
        color = BALL_COLORS[i % len(BALL_COLORS)]
        balls.append(Ball(pos, vel, color))
    return balls

def main():
    hexagons = create_hexagons()
    balls = create_balls(hexagons[-1])
    
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 更新六边形旋转
        for hexagon in hexagons:
            hexagon.update()

        # 更新小球位置
        for ball in balls:
            ball.update()
            # 对每个六边形的各条边进行碰撞检测
            for hexagon in hexagons:
                vertices = hexagon.get_vertices()
                for i in range(6):
                    # 如果该边缺失则跳过
                    if hexagon.missing_edge is not None and i == hexagon.missing_edge:
                        continue
                    a = vertices[i]
                    b = vertices[(i+1)%6]
                    ball.collide_with_line(a, b)

        screen.fill(BG_COLOR)
        # 绘制六边形（从外到内绘制，保证内层在上面）
        for hexagon in hexagons:
            hexagon.draw(screen)
        # 绘制小球
        for ball in balls:
            ball.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()