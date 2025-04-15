import pygame
import numpy as np
import math
from typing import List, Tuple
import random

# 初始化pygame
pygame.init()

# 配置参数
WINDOW_SIZE = (800, 800)
BACKGROUND_COLOR = (0, 0, 0)
FPS = 60

# 可调参数
class Config:
    GRAVITY = 0.5
    FRICTION = 0.99
    BALL_RADIUS = 10
    HEXAGON_ROTATION_SPEEDS = [0.5, 1.0, 1.5]  # 每个六边形的旋转速度
    HEXAGON_SIZES = [100, 200, 300]  # 从内到外的六边形大小
    BALL_COLORS = [
        (255, 0, 0),    # 红
        (0, 255, 0),    # 绿
        (0, 0, 255),    # 蓝
        (255, 255, 0),  # 黄
        (255, 0, 255)   # 紫
    ]

class Ball:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        self.dx = random.uniform(-5, 5)
        self.dy = random.uniform(-5, 5)
        
    def update(self):
        # 应用重力
        self.dy += Config.GRAVITY
        
        # 应用摩擦力
        self.dx *= Config.FRICTION
        self.dy *= Config.FRICTION
        
        # 更新位置
        self.x += self.dx
        self.y += self.dy
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), Config.BALL_RADIUS)

class Hexagon:
    def __init__(self, size: float, rotation_speed: float):
        self.size = size
        self.rotation_speed = rotation_speed
        self.angle = 0
        self.missing_wall = random.randint(0, 5)  # 随机选择缺失的边
        
    def get_points(self) -> List[Tuple[float, float]]:
        points = []
        center_x, center_y = WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2
        
        for i in range(6):
            angle = math.radians(self.angle + i * 60)
            x = center_x + self.size * math.cos(angle)
            y = center_y + self.size * math.sin(angle)
            points.append((x, y))
        
        return points
    
    def update(self):
        self.angle += self.rotation_speed
        
    def draw(self, screen):
        points = self.get_points()
        
        # 绘制除了缺失边之外的所有边
        for i in range(6):
            if i != self.missing_wall:
                start = points[i]
                end = points[(i + 1) % 6]
                pygame.draw.line(screen, (255, 255, 255), start, end, 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Bouncing Balls in Rotating Hexagons")
        self.clock = pygame.time.Clock()
        
        # 创建六边形
        self.hexagons = [
            Hexagon(size, speed)
            for size, speed in zip(Config.HEXAGON_SIZES, Config.HEXAGON_ROTATION_SPEEDS)
        ]
        
        # 创建小球（从最内层六边形的中心开始）
        center_x, center_y = WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2
        self.balls = [
            Ball(center_x, center_y, color)
            for color in Config.BALL_COLORS
        ]
        
    def check_collision(self, ball: Ball, points: List[Tuple[float, float]], missing_wall: int):
        for i in range(6):
            if i == missing_wall:
                continue
                
            p1 = points[i]
            p2 = points[(i + 1) % 6]
            
            # 计算小球到线段的距离
            wall_vector = pygame.math.Vector2(p2[0] - p1[0], p2[1] - p1[1])
            ball_to_wall_start = pygame.math.Vector2(ball.x - p1[0], ball.y - p1[1])
            
            wall_length = wall_vector.length()
            if wall_length == 0:
                continue
                
            # 标准化墙向量
            wall_unit = wall_vector / wall_length
            
            # 计算投影长度
            projection_length = ball_to_wall_start.dot(wall_unit)
            
            if 0 <= projection_length <= wall_length:
                # 计算垂直距离
                perpendicular_vector = ball_to_wall_start - wall_unit * projection_length
                distance = perpendicular_vector.length()
                
                if distance < Config.BALL_RADIUS:
                    # 碰撞发生，计算反弹
                    normal = perpendicular_vector.normalize()
                    velocity = pygame.math.Vector2(ball.dx, ball.dy)
                    reflection = velocity.reflect(normal)
                    
                    ball.dx = reflection.x
                    ball.dy = reflection.y
                    
                    # 稍微将球推离墙壁以防止粘着
                    push_distance = (Config.BALL_RADIUS - distance + 1)
                    ball.x += normal.x * push_distance
                    ball.y += normal.y * push_distance
    
    def run(self):
        running = True
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            # 更新
            for hexagon in self.hexagons:
                hexagon.update()
                
            for ball in self.balls:
                ball.update()
                # 检查与每个六边形的碰撞
                for hexagon in self.hexagons:
                    self.check_collision(ball, hexagon.get_points(), hexagon.missing_wall)
            
            # 绘制
            self.screen.fill(BACKGROUND_COLOR)
            
            # 从外到内绘制六边形
            for hexagon in reversed(self.hexagons):
                hexagon.draw(self.screen)
                
            # 绘制小球
            for ball in self.balls:
                ball.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()