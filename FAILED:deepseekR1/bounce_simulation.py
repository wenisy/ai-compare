import pygame
import math
import random
from pygame.locals import *

# 可调参数
SETTINGS = {
    "gravity": 0.3,
    "friction": 0.985,
    "ball_radius": 8,
    "hex_sizes": [400, 300, 200, 100],  # 从外到内的六边形尺寸
    "rotation_speeds": [0.3, -0.5, 0.7, -0.4],  # 各层旋转速度
    "colors": [(255,50,50), (50,255,50), (50,50,255), (255,255,50), (50,255,255)]
}

class Hexagon:
    def __init__(self, size, rot_speed, level):
        self.size = size
        self.angle = 0
        self.rot_speed = rot_speed
        self.level = level
        self.missing_wall = random.randint(0, 5) if level > 0 else None
        
    def get_points(self, center):
        points = []
        for i in range(6):
            if i == self.missing_wall:
                continue
            angle_deg = 60 * i + self.angle
            x = center[0] + self.size * math.cos(math.radians(angle_deg))
            y = center[1] + self.size * math.sin(math.radians(angle_deg))
            points.append((x, y))
        return points
    
    def update(self):
        self.angle += self.rot_speed

class Ball:
    def __init__(self, color):
        self.pos = [0, 0]
        self.vel = [random.uniform(-3,3), random.uniform(-3,3)]
        self.color = color
        self.trail = []
        
    def apply_physics(self):
        self.vel[1] += SETTINGS["gravity"]
        self.vel = [v * SETTINGS["friction"] for v in self.vel]
        self.pos = [self.pos[0]+self.vel[0], self.pos[1]+self.vel[1]]
        
        if len(self.trail) > 20:
            self.trail.pop(0)
        self.trail.append(tuple(self.pos))
        
    def check_collision(self, hexagons, screen_rect):
        # 边界碰撞
        if not screen_rect.collidepoint(self.pos):
            self.pos = [screen_rect.centerx, screen_rect.centery]
            return
            
        # 六边形碰撞检测
        for hexagon in hexagons:
            center = screen_rect.center
            vec = (self.pos[0]-center[0], self.pos[1]-center[1])
            dist = math.hypot(vec[0], vec[1])
            
            if hexagon.level == 0:  # 最外层
                if dist > hexagon.size:
                    angle = math.atan2(vec[1], vec[0])
                    self.pos = [
                        center[0] + hexagon.size * math.cos(angle),
                        center[1] + hexagon.size * math.sin(angle)
                    ]
                    tangent = [-vec[1], vec[0]]
                    vel_mag = math.hypot(self.vel[0], self.vel[1])
                    self.vel = [tangent[0]*vel_mag/hexagon.size, tangent[1]*vel_mag/hexagon.size]
            else:  # 内层
                pass  # 根据缺失边处理逻辑

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF)
    clock = pygame.time.Clock()
    
    hexagons = [Hexagon(size, speed, i) 
               for i, (size, speed) in enumerate(zip(SETTINGS["hex_sizes"], SETTINGS["rotation_speeds"]))]
    
    balls = [Ball(SETTINGS["colors"][i]) for i in range(5)]
    for b in balls:
        b.pos = [400, 300]
    
    running = True
    while running:
        screen.fill((0,0,0))
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                
        # 更新六边形
        for h in hexagons:
            h.update()
            
        # 绘制六边形
        for h in hexagons:
            pts = h.get_points(screen.get_rect().center)
            if len(pts) > 1:
                pygame.draw.lines(screen, (200,200,200), True, pts, 2)
        
        # 更新球体物理
        for b in balls:
            b.apply_physics()
            b.check_collision(hexagons, screen.get_rect())
            
            # 绘制轨迹
            if len(b.trail) >= 2:
                pygame.draw.lines(screen, b.color, False, b.trail, 3)
            pygame.draw.circle(screen, b.color, [int(b.pos[0]), int(b.pos[1])], SETTINGS["ball_radius"])
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()