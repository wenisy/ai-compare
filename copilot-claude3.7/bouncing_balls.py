import pygame
import sys
import math
import random
import numpy as np
from pygame.locals import *

# 初始化 Pygame
pygame.init()

# 设置窗口
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("嵌套旋转六边形中的弹跳球")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BALL_COLORS = [
    (255, 0, 0),    # 红色
    (0, 255, 0),    # 绿色
    (0, 0, 255),    # 蓝色
    (255, 255, 0),  # 黄色
    (255, 0, 255)   # 紫色
]

# 可调参数
class Parameters:
    def __init__(self):
        self.gravity = 0.1
        self.friction = 0.99
        self.num_hexagons = 3
        self.base_size = 300
        self.size_factor = 0.7
        self.rotation_speeds = [0.2, 0.5, 1.0]
        self.ball_radius = 15
        self.ball_count = 5

params = Parameters()
clock = pygame.time.Clock()

# 六边形类
class Hexagon:
    def __init__(self, center, size, rotation_speed, missing_wall=None):
        self.center = center
        self.size = size
        self.rotation_speed = rotation_speed
        self.angle = 0
        self.missing_wall = missing_wall if missing_wall is not None else random.randint(0, 5)
        
    def get_vertices(self):
        vertices = []
        for i in range(6):
            angle = math.radians(self.angle + i * 60)
            x = self.center[0] + self.size * math.cos(angle)
            y = self.center[1] + self.size * math.sin(angle)
            vertices.append((x, y))
        return vertices
    
    def get_walls(self):
        vertices = self.get_vertices()
        walls = []
        for i in range(6):
            if i != self.missing_wall:
                walls.append((vertices[i], vertices[(i+1) % 6]))
        return walls
    
    def update(self):
        self.angle += self.rotation_speed
        if self.angle >= 360:
            self.angle -= 360
    
    def draw(self, surface):
        walls = self.get_walls()
        for wall in walls:
            pygame.draw.line(surface, WHITE, wall[0], wall[1], 2)

# 球类
class Ball:
    def __init__(self, pos, radius, color):
        self.pos = np.array(pos, dtype=float)
        self.vel = np.array([random.uniform(-1, 1), random.uniform(-1, 1)], dtype=float)
        self.radius = radius
        self.color = color
        self.angular_momentum = 0
        
    def update(self, hexagons, params):
        # 应用重力
        self.vel[1] += params.gravity
        
        # 更新位置
        self.pos += self.vel
        
        # 应用摩擦力
        self.vel *= params.friction
        
        # 墙壁碰撞检测
        for hexagon in hexagons:
            walls = hexagon.get_walls()
            for wall in walls:
                self.check_wall_collision(wall, hexagon)
                
        # 限制在屏幕范围内
        if self.pos[0] < self.radius:
            self.pos[0] = self.radius
            self.vel[0] *= -1
        elif self.pos[0] > WIDTH - self.radius:
            self.pos[0] = WIDTH - self.radius
            self.vel[0] *= -1
            
        if self.pos[1] < self.radius:
            self.pos[1] = self.radius
            self.vel[1] *= -1
        elif self.pos[1] > HEIGHT - self.radius:
            self.pos[1] = HEIGHT - self.radius
            self.vel[1] *= -1
    
    def check_wall_collision(self, wall, hexagon):
        p1 = np.array(wall[0])
        p2 = np.array(wall[1])
        
        # 线段向量
        seg_vec = p2 - p1
        seg_len = np.linalg.norm(seg_vec)
        unit_vec = seg_vec / seg_len
        
        # 球到线段起点的向量
        ball_to_p1 = self.pos - p1
        
        # 投影长度
        proj_len = np.dot(ball_to_p1, unit_vec)
        
        # 最近点
        if proj_len < 0:
            closest = p1
        elif proj_len > seg_len:
            closest = p2
        else:
            closest = p1 + unit_vec * proj_len
        
        # 计算距离
        dist_vec = self.pos - closest
        distance = np.linalg.norm(dist_vec)
        
        # 如果距离小于球半径，就发生碰撞
        if distance < self.radius:
            # 计算碰撞法线
            if distance > 0:
                normal = dist_vec / distance
            else:
                normal = np.array([1, 0])  # 防止除以零
            
            # 计算相对速度
            wall_vel = np.array([0, 0])
            if proj_len >= 0 and proj_len <= seg_len:
                # 计算旋转的墙壁的速度
                angle_rad = math.radians(hexagon.angle)
                center_to_hit = closest - np.array(hexagon.center)
                tangent_dir = np.array([-center_to_hit[1], center_to_hit[0]])
                if np.linalg.norm(tangent_dir) > 0:
                    tangent_dir = tangent_dir / np.linalg.norm(tangent_dir)
                    wall_vel = tangent_dir * hexagon.rotation_speed * 0.1
            
            rel_vel = self.vel - wall_vel
            
            # 计算相对速度在法线方向的分量
            normal_vel = np.dot(rel_vel, normal)
            
            # 只有当物体相对靠近时才进行碰撞响应
            if normal_vel < 0:
                # 计算反弹后的速度
                restitution = 0.85  # 弹性系数
                impulse = -(1 + restitution) * normal_vel
                self.vel += impulse * normal
                
                # 考虑旋转墙壁的角动量传递
                if proj_len >= 0 and proj_len <= seg_len:
                    self.angular_momentum += hexagon.rotation_speed * 0.05
                    tangential_component = np.dot(self.vel, tangent_dir) * tangent_dir
                    self.vel += tangential_component * 0.2
                
                # 将球推出墙壁
                penetration = self.radius - distance
                self.pos += normal * penetration
    
    def draw(self, surface):
        pos_int = (int(self.pos[0]), int(self.pos[1]))
        pygame.draw.circle(surface, self.color, pos_int, self.radius)
        pygame.draw.circle(surface, WHITE, pos_int, self.radius, 1)

# 创建嵌套六边形
def create_hexagons(params):
    hexagons = []
    center = (WIDTH//2, HEIGHT//2)
    
    for i in range(params.num_hexagons):
        size = params.base_size * (params.size_factor ** i)
        speed = params.rotation_speeds[i % len(params.rotation_speeds)]
        
        # 最外层六边形没有缺口
        missing_wall = None if i == 0 else random.randint(0, 5)
        
        hexagon = Hexagon(center, size, speed, missing_wall)
        hexagons.append(hexagon)
    
    return hexagons

# 创建球
def create_balls(params, innermost_hexagon):
    balls = []
    center = innermost_hexagon.center
    radius = innermost_hexagon.size * 0.5
    
    for i in range(params.ball_count):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius)
        pos = (
            center[0] + distance * math.cos(angle),
            center[1] + distance * math.sin(angle)
        )
        ball = Ball(pos, params.ball_radius, BALL_COLORS[i % len(BALL_COLORS)])
        balls.append(ball)
    
    return balls

# 主循环
def main():
    # 创建嵌套六边形（从外到内）
    hexagons = create_hexagons(params)
    
    # 创建球（初始在最内层六边形内）
    balls = create_balls(params, hexagons[-1])
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                # 调整参数
                elif event.key == K_UP:
                    params.gravity += 0.05
                elif event.key == K_DOWN:
                    params.gravity = max(0, params.gravity - 0.05)
                elif event.key == K_RIGHT:
                    for i in range(len(params.rotation_speeds)):
                        params.rotation_speeds[i] *= 1.1
                elif event.key == K_LEFT:
                    for i in range(len(params.rotation_speeds)):
                        params.rotation_speeds[i] *= 0.9
        
        # 清空屏幕
        screen.fill(BLACK)
        
        # 更新并绘制六边形
        for hexagon in hexagons:
            hexagon.update()
            hexagon.draw(screen)
        
        # 更新并绘制球
        for ball in balls:
            ball.update(hexagons, params)
            ball.draw(screen)
        
        # 显示参数
        font = pygame.font.Font(None, 30)
        text_surface = font.render(f"重力: {params.gravity:.2f} | 摩擦: {params.friction:.2f} | 旋转速度: {params.rotation_speeds[0]:.2f}", True, WHITE)
        text_rect = text_surface.get_rect(topleft=(10, 10))
        screen.blit(text_surface, text_rect)
        
        help_text = font.render("按方向键调整参数: ↑↓ 调整重力, ←→ 调整旋转速度", True, WHITE)
        help_rect = help_text.get_rect(topleft=(10, 40))
        screen.blit(help_text, help_rect)
        
        # 更新显示
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()