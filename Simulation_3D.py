import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moteur Physique Isométrique avec plusieurs balles")
clock = pygame.time.Clock()

TILE_WIDTH = 64
TILE_HEIGHT = 32
GRAVITY = 98.1
FLOOR_Z = 0

WHITE = (255, 255, 255)
GREY = (180, 180, 180)
AXIS_X_COLOR = (255, 0, 0)
AXIS_Y_COLOR = (0, 255, 0)
AXIS_Z_COLOR = (0, 0, 255)
GRID_COLOR = (150, 150, 150, 70)  # gris transparent

def iso_project(x, y, z):
    screen_x = WIDTH // 2 + (x - y) * TILE_WIDTH // 2
    screen_y = HEIGHT // 2 + (x + y) * TILE_HEIGHT // 2 - z
    return int(screen_x), int(screen_y)

class Ball:
    def __init__(self, x, y, z, color, radius=10, vx=0, vy=0, vz=0, ax=0, ay=0, az=0):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.ax = ax
        self.ay = ay
        self.az = az
        self.radius = radius
        self.color = color

    def apply_gravity(self, dt):
        self.az -= GRAVITY * dt

    def update(self, dt):
        # Appliquer accélération à la vitesse
        self.vx += self.ax * dt
        self.vy += self.ay * dt
        self.vz += self.az * dt

        # Appliquer vitesse à la position
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt

        # Collision avec le sol
        if self.z <= FLOOR_Z:
            self.z = FLOOR_Z
            self.vz *= -0.8
            self.vx *= 0.9
            self.vy *= 0.9
            if abs(self.vz) < 1:
                self.vz = 0
                self.az = 0



    def draw(self, surface):
        px, py = iso_project(self.x, self.y, self.z)
        shadow_x, shadow_y = iso_project(self.x, self.y, 0)
        pygame.draw.circle(surface, GREY, (shadow_x, shadow_y), self.radius)  # ombre
        pygame.draw.circle(surface, self.color, (px, py), self.radius)

def draw_axes(surface):
    origin = iso_project(0, 0, 0)
    x_axis = iso_project(3, 0, 0)
    y_axis = iso_project(0, 3, 0)
    z_axis = iso_project(0, 0, 50)

    pygame.draw.line(surface, AXIS_X_COLOR, origin, x_axis, 3)
    pygame.draw.line(surface, AXIS_Y_COLOR, origin, y_axis, 3)
    pygame.draw.line(surface, AXIS_Z_COLOR, origin, z_axis, 3)

    font = pygame.font.SysFont(None, 20)
    surface.blit(font.render("X", True, AXIS_X_COLOR), x_axis)
    surface.blit(font.render("Y", True, AXIS_Y_COLOR), y_axis)
    surface.blit(font.render("Z", True, AXIS_Z_COLOR), (z_axis[0]+5, z_axis[1]))

def draw_grid(surface, size=10):
    grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    for i in range(size + 1):
        start = iso_project(0, i, 0)
        end = iso_project(size, i, 0)
        pygame.draw.line(grid_surface, GRID_COLOR, start, end, 1)

        start = iso_project(i, 0, 0)
        end = iso_project(i, size, 0)
        pygame.draw.line(grid_surface, GRID_COLOR, start, end, 1)

    surface.blit(grid_surface, (0, 0))

# Création de plusieurs balles avec couleurs, vitesses, accélérations différentes
balls = [
    Ball(x=0, y=0, z=100, color=(255, 0, 0), vz=0, radius=12),
    Ball(x=0, y=0, z=100, color=(0, 255, 0), vx=-0.5, vy=0.5, vz=0, radius=15),
    Ball(x=0, y=0, z=100, color=(0, 0, 255), vx=0.5, vy=0.5, vz=0, az=0, radius=10),
]

while True:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    for ball in balls:
        ball.apply_gravity(dt)
        ball.update(dt)

    screen.fill(WHITE)
    draw_grid(screen, size=15)
    draw_axes(screen)

    for ball in balls:
        ball.draw(screen)

    pygame.display.flip()
