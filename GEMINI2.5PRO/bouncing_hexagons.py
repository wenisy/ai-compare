import pygame
import math
import random

# --- Adjustable Parameters ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUM_BALLS = 5
BALL_RADIUS = 10
GRAVITY = 0.1
FRICTION = 0.99 # Energy retained after bounce
HEXAGON_LAYERS = 3
INITIAL_HEX_RADIUS = 50
HEX_RADIUS_STEP = 50 # Increase in radius per layer
HEX_THICKNESS = 2
ROTATION_SPEEDS = [0.005, -0.003, 0.001] # Radians per frame for each layer (outermost first)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
BACKGROUND_COLOR = (0, 0, 0)
HEXAGON_COLOR = (255, 255, 255)
# ---------------------------

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bouncing Balls in Rotating Hexagons")
clock = pygame.time.Clock()
# --------------------

# --- Helper Functions ---
def rotate_point(point, angle, center):
    """Rotates a point around a center."""
    ox, oy = center
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def get_hexagon_vertices(center_x, center_y, radius, rotation_angle):
    """Calculates the vertices of a hexagon."""
    vertices = []
    for i in range(6):
        angle = math.pi / 3 * i + rotation_angle
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices

def distance_point_segment(p, a, b):
    """Calculates the shortest distance between a point p and a line segment ab."""
    px, py = p
    ax, ay = a
    bx, by = b

    # Vector ab
    ab_x = bx - ax
    ab_y = by - ay

    # Vector ap
    ap_x = px - ax
    ap_y = py - ay

    ab_squared = ab_x**2 + ab_y**2
    if ab_squared == 0: # a and b are the same point
        return math.dist(p, a), a # Distance to point a

    # Project ap onto ab
    t = (ap_x * ab_x + ap_y * ab_y) / ab_squared
    t = max(0, min(1, t)) # Clamp t to the segment

    # Closest point on the line segment
    closest_x = ax + t * ab_x
    closest_y = ay + t * ab_y
    closest_point = (closest_x, closest_y)

    dist = math.dist(p, closest_point)
    return dist, closest_point

def reflect_velocity(vel, wall_normal):
    """Reflects velocity vector off a wall normal."""
    vx, vy = vel
    nx, ny = wall_normal
    # Normalize normal vector
    norm_len = math.sqrt(nx**2 + ny**2)
    if norm_len == 0: return vel # Avoid division by zero
    nx /= norm_len
    ny /= norm_len

    # v_reflected = v - 2 * (v . n) * n
    dot_product = vx * nx + vy * ny
    reflected_vx = vx - 2 * dot_product * nx
    reflected_vy = vy - 2 * dot_product * ny
    return reflected_vx * FRICTION, reflected_vy * FRICTION
# ----------------------

# --- Classes ---
class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)

    def update(self, hexagons):
        # Apply gravity
        self.vy += GRAVITY

        # Move ball
        self.x += self.vx
        self.y += self.vy

        # Collision with hexagons
        collided = False
        for i, hexagon in enumerate(hexagons):
            collision_data = hexagon.check_collision(self)
            if collision_data:
                collided = True
                dist, closest_point, wall_start, wall_end, is_missing = collision_data

                if is_missing: # Pass through missing wall
                    continue

                # --- Collision Response ---
                # 1. Correct position (move ball outside the wall)
                overlap = self.radius - dist
                if overlap > 0:
                    # Vector from closest point on wall to ball center
                    correction_x = self.x - closest_point[0]
                    correction_y = self.y - closest_point[1]
                    correction_len = math.sqrt(correction_x**2 + correction_y**2)

                    if correction_len > 0:
                        # Move ball along this vector by the overlap amount
                        move_x = (correction_x / correction_len) * overlap
                        move_y = (correction_y / correction_len) * overlap
                        self.x += move_x
                        self.y += move_y

                # 2. Reflect velocity
                # Wall vector
                wall_dx = wall_end[0] - wall_start[0]
                wall_dy = wall_end[1] - wall_start[1]
                # Normal vector (pointing outwards for hexagon)
                # Rotate wall vector 90 degrees clockwise for inner normal, then negate for outer
                normal_x = wall_dy
                normal_y = -wall_dx

                # Ensure normal points away from hexagon center relative to ball
                center_to_ball_x = self.x - hexagon.center_x
                center_to_ball_y = self.y - hexagon.center_y
                if (center_to_ball_x * normal_x + center_to_ball_y * normal_y) < 0:
                    normal_x *= -1
                    normal_y *= -1


                self.vx, self.vy = reflect_velocity((self.vx, self.vy), (normal_x, normal_y))

                # Add angular momentum effect (simplified)
                # Calculate wall velocity at collision point
                wall_angle_speed = hexagon.rotation_speed
                dist_from_center = math.dist(closest_point, (hexagon.center_x, hexagon.center_y))
                # Tangential velocity = angular_speed * distance
                wall_tangential_speed = wall_angle_speed * dist_from_center
                # Wall velocity vector (tangent to rotation)
                angle_to_point = math.atan2(closest_point[1] - hexagon.center_y, closest_point[0] - hexagon.center_x)
                tangent_angle = angle_to_point + math.pi / 2 # Perpendicular to radius
                wall_vx = wall_tangential_speed * math.cos(tangent_angle)
                wall_vy = wall_tangential_speed * math.sin(tangent_angle)

                # Add a fraction of the wall's velocity to the ball (imparts spin/kick)
                self.vx += wall_vx * 0.1 # Adjust coefficient for effect strength
                self.vy += wall_vy * 0.1

                break # Handle one collision per frame for simplicity


        # Keep balls roughly within the outermost hexagon (simple boundary)
        max_r = INITIAL_HEX_RADIUS + HEX_RADIUS_STEP * (HEXAGON_LAYERS -1) + 20
        dist_sq = (self.x - SCREEN_WIDTH/2)**2 + (self.y - SCREEN_HEIGHT/2)**2
        if dist_sq > max_r**2 :
             self.vx, self.vy = reflect_velocity((self.vx, self.vy), (SCREEN_WIDTH/2 - self.x, SCREEN_HEIGHT/2 - self.y))
             # Move back slightly
             self.x += self.vx * 0.1
             self.y += self.vy * 0.1


    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Hexagon:
    def __init__(self, center_x, center_y, radius, rotation_speed, thickness, is_outermost=False):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.rotation_speed = rotation_speed
        self.thickness = thickness
        self.rotation_angle = random.uniform(0, 2 * math.pi) # Initial random angle
        self.vertices = []
        self.missing_wall_index = -1 if is_outermost else random.randint(0, 5)
        self.update_vertices()

    def update_vertices(self):
        self.rotation_angle += self.rotation_speed
        self.vertices = get_hexagon_vertices(self.center_x, self.center_y, self.radius, self.rotation_angle)

    def check_collision(self, ball):
        """Checks collision between the ball and the hexagon walls."""
        min_dist_to_wall = float('inf')
        closest_wall_data = None

        for i in range(6):
            start_point = self.vertices[i]
            end_point = self.vertices[(i + 1) % 6]

            dist, closest_point_on_segment = distance_point_segment((ball.x, ball.y), start_point, end_point)

            if dist < min_dist_to_wall:
                 min_dist_to_wall = dist
                 is_missing = (i == self.missing_wall_index)
                 closest_wall_data = (dist, closest_point_on_segment, start_point, end_point, is_missing)


        if min_dist_to_wall <= ball.radius:
            return closest_wall_data
        return None


    def draw(self, surface):
        for i in range(6):
            if i != self.missing_wall_index:
                start_point = self.vertices[i]
                end_point = self.vertices[(i + 1) % 6]
                pygame.draw.line(surface, HEXAGON_COLOR, start_point, end_point, self.thickness)
# -------------

# --- Game Objects ---
center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
hexagons = []
for i in range(HEXAGON_LAYERS):
    radius = INITIAL_HEX_RADIUS + i * HEX_RADIUS_STEP
    speed = ROTATION_SPEEDS[i % len(ROTATION_SPEEDS)] # Cycle through speeds if fewer provided
    is_outer = (i == HEXAGON_LAYERS - 1)
    hexagons.append(Hexagon(center_x, center_y, radius, speed, HEX_THICKNESS, is_outermost=is_outer))

balls = []
# Start balls near the center of the innermost hexagon
innermost_radius = INITIAL_HEX_RADIUS / 2
for i in range(NUM_BALLS):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(0, innermost_radius)
    start_x = center_x + dist * math.cos(angle)
    start_y = center_y + dist * math.sin(angle)
    balls.append(Ball(start_x, start_y, BALL_RADIUS, COLORS[i % len(COLORS)]))
# ------------------

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Updates ---
    for hexagon in hexagons:
        hexagon.update_vertices()
    for ball in balls:
        ball.update(hexagons) # Pass all hexagons for collision checks
    # ---------------

    # --- Drawing ---
    screen.fill(BACKGROUND_COLOR)
    for hexagon in hexagons:
        hexagon.draw(screen)
    for ball in balls:
        ball.draw(screen)
    # ---------------

    pygame.display.flip()
    clock.tick(60) # Limit frame rate

pygame.quit()
# -----------------