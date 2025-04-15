import pygame
import pymunk
import math
import random
import numpy as np
from typing import List, Tuple

# Initialize Pygame and Pymunk
pygame.init()
space = pymunk.Space()
space.gravity = (0, 981)  # Gravity in pixels/s^2

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
FPS = 60
BALL_RADIUS = 10
FRICTION = 0.7
ELASTICITY = 0.95
BALL_COLORS = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255)]

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rotating Hexagons with Bouncing Balls")
clock = pygame.time.Clock()

class RotatingHexagon:
    def __init__(self, center: Tuple[float, float], radius: float, rotation_speed: float, missing_wall: int = None):
        self.center = center
        self.radius = radius
        self.rotation_speed = rotation_speed
        self.angle = 0
        self.missing_wall = missing_wall
        self.lines = []
        self.create_hexagon()
    
    def create_hexagon(self):
        # Clear existing lines
        for line in self.lines:
            if line in space.shapes:
                space.remove(line)
        self.lines.clear()
        
        # Create new hexagon walls
        for i in range(6):
            if i == self.missing_wall:
                continue
                
            angle1 = math.pi / 3 * i + self.angle
            angle2 = math.pi / 3 * (i + 1) + self.angle
            
            x1 = self.center[0] + self.radius * math.cos(angle1)
            y1 = self.center[1] + self.radius * math.sin(angle1)
            x2 = self.center[0] + self.radius * math.cos(angle2)
            y2 = self.center[1] + self.radius * math.sin(angle2)
            
            shape = pymunk.Segment(space.static_body, (x1, y1), (x2, y2), 2)
            shape.friction = FRICTION
            shape.elasticity = ELASTICITY
            space.add(shape)
            self.lines.append(shape)
    
    def update(self):
        self.angle += self.rotation_speed
        self.create_hexagon()
    
    def draw(self, screen):
        for line in self.lines:
            pygame.draw.line(screen, (255, 255, 255), 
                           line.a, line.b, 2)

class Ball:
    def __init__(self, pos: Tuple[float, float], color: Tuple[int, int, int]):
        self.mass = 1
        self.radius = BALL_RADIUS
        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.friction = FRICTION
        self.shape.elasticity = ELASTICITY
        self.color = color
        space.add(self.body, self.shape)
    
    def draw(self, screen):
        pos = self.body.position
        pygame.draw.circle(screen, self.color, 
                         (int(pos.x), int(pos.y)), self.radius)

def main():
    # Create nested hexagons
    center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    hexagons = []
    num_hexagons = 3
    for i in range(num_hexagons):
        radius = 100 * (i + 1)
        rotation_speed = 0.02 * (num_hexagons - i)  # Outer hexagons rotate slower
        missing_wall = random.randint(0, 5) if i < num_hexagons - 1 else None
        hexagon = RotatingHexagon(center, radius, rotation_speed, missing_wall)
        hexagons.append(hexagon)
    
    # Create balls
    balls = []
    for i in range(5):
        pos = (center[0] + random.randint(-30, 30), 
               center[1] + random.randint(-30, 30))
        ball = Ball(pos, BALL_COLORS[i])
        balls.append(ball)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update physics
        space.step(1/FPS)
        
        # Update hexagons
        for hexagon in hexagons:
            hexagon.update()
        
        # Draw
        screen.fill((0, 0, 0))
        for hexagon in hexagons:
            hexagon.draw(screen)
        for ball in balls:
            ball.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()