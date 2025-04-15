#!/usr/bin/env python3
"""
Bouncing Balls in Rotating Hexagons Simulation
----------------------------------------------
A visual simulation of colored balls bouncing within nested, rotating hexagons.
Each hexagon rotates at a different speed and has one missing wall (except the outermost).
Physics includes gravity, friction, and realistic collisions.
"""

import pygame
import sys
import math
import random
import numpy as np
from pygame.locals import *

# Initialize pygame
pygame.init()

# Configuration parameters (adjustable)
WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)
FPS = 60

# Physics parameters (adjustable)
GRAVITY = 0.2
FRICTION = 0.99
ELASTICITY = 0.8
BALL_RADIUS = 10
NUM_BALLS = 5
NUM_HEXAGONS = 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
BALL_COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
]

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Balls in Rotating Hexagons")
clock = pygame.time.Clock()


class Hexagon:
    def __init__(self, center, size, rotation_speed, missing_wall=None):
        self.center = center
        self.size = size
        self.rotation_speed = rotation_speed  # degrees per frame
        self.angle = 0
        self.missing_wall = missing_wall  # Index of the missing wall (0-5)
        
    def get_vertices(self):
        vertices = []
        for i in range(6):
            angle_rad = math.radians(self.angle + i * 60)
            x = self.center[0] + self.size * math.cos(angle_rad)
            y = self.center[1] + self.size * math.sin(angle_rad)
            vertices.append((x, y))
        return vertices
    
    def get_walls(self):
        vertices = self.get_vertices()
        walls = []
        for i in range(6):
            if i != self.missing_wall:  # Skip the missing wall
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


class Ball:
    def __init__(self, x, y, radius, color):
        self.pos = np.array([float(x), float(y)])
        self.vel = np.array([0.0, 0.0])
        self.radius = radius
        self.color = color
        self.mass = radius * 0.1
    
    def update(self):
        # Apply gravity
        self.vel[1] += GRAVITY
        
        # Apply friction
        self.vel *= FRICTION
        
        # Update position
        self.pos += self.vel
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)
        
    def check_boundary_collision(self):
        # Bounce off screen edges (as a fallback)
        if self.pos[0] - self.radius < 0:
            self.pos[0] = self.radius
            self.vel[0] = -self.vel[0] * ELASTICITY
        elif self.pos[0] + self.radius > WIDTH:
            self.pos[0] = WIDTH - self.radius
            self.vel[0] = -self.vel[0] * ELASTICITY
            
        if self.pos[1] - self.radius < 0:
            self.pos[1] = self.radius
            self.vel[1] = -self.vel[1] * ELASTICITY
        elif self.pos[1] + self.radius > HEIGHT:
            self.pos[1] = HEIGHT - self.radius
            self.vel[1] = -self.vel[1] * ELASTICITY
    
    def check_ball_collision(self, other_ball):
        # Vector from this ball to the other ball
        delta_pos = other_ball.pos - self.pos
        distance = np.linalg.norm(delta_pos)
        
        # Check if balls are colliding
        if distance < self.radius + other_ball.radius:
            # Normalize the collision vector
            if distance == 0:  # Avoid division by zero
                collision_vector = np.array([1.0, 0.0])
            else:
                collision_vector = delta_pos / distance
            
            # Calculate relative velocity
            delta_vel = other_ball.vel - self.vel
            
            # Calculate impulse
            impulse = 2 * (np.dot(delta_vel, collision_vector)) / (self.mass + other_ball.mass)
            
            # Apply impulse to both balls
            self.vel += impulse * other_ball.mass * collision_vector * ELASTICITY
            other_ball.vel -= impulse * self.mass * collision_vector * ELASTICITY
            
            # Separate the balls to prevent sticking
            overlap = (self.radius + other_ball.radius - distance) / 2
            self.pos -= overlap * collision_vector
            other_ball.pos += overlap * collision_vector
    
    def check_wall_collision(self, wall):
        # Wall is defined by two points: wall[0] and wall[1]
        wall_vector = np.array([wall[1][0] - wall[0][0], wall[1][1] - wall[0][1]])
        wall_length = np.linalg.norm(wall_vector)
        wall_unit = wall_vector / wall_length
        
        # Vector from wall start to ball
        ball_vector = np.array([self.pos[0] - wall[0][0], self.pos[1] - wall[0][1]])
        
        # Project ball vector onto wall vector
        projection_length = np.dot(ball_vector, wall_unit)
        
        # Find closest point on wall to ball
        if projection_length < 0:
            closest_point = np.array(wall[0])
        elif projection_length > wall_length:
            closest_point = np.array(wall[1])
        else:
            closest_point = np.array(wall[0]) + projection_length * wall_unit
        
        # Vector from closest point to ball
        closest_to_ball = self.pos - closest_point
        distance = np.linalg.norm(closest_to_ball)
        
        # Check if ball is colliding with wall
        if distance < self.radius:
            # Normalize the collision vector
            if distance == 0:  # Avoid division by zero
                collision_normal = np.array([wall_unit[1], -wall_unit[0]])  # Perpendicular to wall
            else:
                collision_normal = closest_to_ball / distance
            
            # Calculate reflection
            dot_product = np.dot(self.vel, collision_normal)
            self.vel -= (1 + ELASTICITY) * dot_product * collision_normal
            
            # Move ball outside of wall
            self.pos += (self.radius - distance) * collision_normal
            
            # Add some angular momentum effect from the rotating wall
            # This simulates the wall "pushing" the ball as it rotates
            tangent = np.array([-collision_normal[1], collision_normal[0]])
            self.vel += tangent * 0.5  # Adjust this value for more/less effect


def create_hexagons(num_hexagons):
    hexagons = []
    max_size = min(WIDTH, HEIGHT) * 0.4
    
    for i in range(num_hexagons):
        size = max_size * (1 - i * 0.25)
        rotation_speed = random.uniform(0.2, 1.0) * (-1 if i % 2 == 0 else 1)
        
        # Only the outermost hexagon has no missing wall
        missing_wall = None if i == 0 else random.randint(0, 5)
        
        hexagon = Hexagon(CENTER, size, rotation_speed, missing_wall)
        hexagons.append(hexagon)
    
    return hexagons


def create_balls(num_balls, innermost_hexagon):
    balls = []
    
    # Get the size of the innermost hexagon
    inner_size = innermost_hexagon.size * 0.8
    
    for i in range(num_balls):
        # Place balls randomly within the innermost hexagon
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, inner_size * 0.7)
        
        x = CENTER[0] + distance * math.cos(angle)
        y = CENTER[1] + distance * math.sin(angle)
        
        ball = Ball(x, y, BALL_RADIUS, BALL_COLORS[i % len(BALL_COLORS)])
        balls.append(ball)
    
    return balls


def main():
    # Create hexagons (from outer to inner)
    hexagons = create_hexagons(NUM_HEXAGONS)
    
    # Create balls inside the innermost hexagon
    balls = create_balls(NUM_BALLS, hexagons[-1])
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Update and draw hexagons
        for hexagon in hexagons:
            hexagon.update()
            hexagon.draw(screen)
        
        # Update and draw balls
        for i, ball in enumerate(balls):
            ball.update()
            
            # Check for collisions with walls
            for hexagon in hexagons:
                for wall in hexagon.get_walls():
                    ball.check_wall_collision(wall)
            
            # Check for collisions with other balls
            for j in range(i + 1, len(balls)):
                ball.check_ball_collision(balls[j])
            
            # Fallback boundary check
            ball.check_boundary_collision()
            
            # Draw the ball
            ball.draw(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
