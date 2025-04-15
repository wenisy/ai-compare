import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Balls in Rotating Hexagons")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BALL_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

# Parameters
gravity = 0.1
friction = 0.99
hexagon_sizes = [200, 150, 100, 50]
rotation_speeds = [0.5, -0.3, 0.7, -0.4]
missing_walls = [random.randint(0, 5) for _ in range(len(hexagon_sizes) - 1)]

# Ball class
class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)

    def move(self):
        self.vy += gravity
        self.vx *= friction
        self.vy *= friction
        self.x += self.vx
        self.y += self.vy

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# Hexagon class
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

    def draw(self):
        points = []
        for i in range(6):
            if i == self.missing_wall:
                continue
            angle_rad = math.radians(self.angle + i * 60)
            px = self.x + self.size * math.cos(angle_rad)
            py = self.y + self.size * math.sin(angle_rad)
            points.append((px, py))
        pygame.draw.polygon(screen, WHITE, points, 1)

# Initialize hexagons and balls
hexagons = [Hexagon(WIDTH // 2, HEIGHT // 2, size, speed, missing_wall)
            for size, speed, missing_wall in zip(hexagon_sizes, rotation_speeds, missing_walls)]
balls = [Ball(WIDTH // 2, HEIGHT // 2, 10, color) for color in BALL_COLORS]

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update and draw hexagons
    for hexagon in hexagons:
        hexagon.rotate()
        hexagon.draw()

    # Update and draw balls
    for ball in balls:
        ball.move()
        ball.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()