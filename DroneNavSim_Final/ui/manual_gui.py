
import pygame
import numpy as np
import sys
import random

# Constants
GRID_SIZE = 30
CELL_SIZE = 20
MARGIN = 1
WIDTH = GRID_SIZE * (CELL_SIZE + MARGIN) + 200
HEIGHT = GRID_SIZE * (CELL_SIZE + MARGIN)
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (150, 150, 150)

# Initialize terrain
def generate_terrain(grid_size, obstacle_ratio=0.25):
    terrain = np.zeros((grid_size, grid_size), dtype=int)
    num_obstacles = int(obstacle_ratio * grid_size * grid_size)
    for _ in range(num_obstacles):
        x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
        terrain[y][x] = 1
    return terrain

# Game setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Manual Drone Navigation")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

terrain = generate_terrain(GRID_SIZE)
drone_pos = [0, 0]
target_pos = [random.randint(GRID_SIZE//2, GRID_SIZE-1), random.randint(GRID_SIZE//2, GRID_SIZE-1)]
while terrain[target_pos[1]][target_pos[0]] == 1:
    target_pos = [random.randint(GRID_SIZE//2, GRID_SIZE-1), random.randint(GRID_SIZE//2, GRID_SIZE-1)]
path = []

def draw_grid():
    screen.fill(GRAY)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * (CELL_SIZE + MARGIN), y * (CELL_SIZE + MARGIN), CELL_SIZE, CELL_SIZE)
            color = WHITE
            if terrain[y][x] == 1:
                color = BLACK
            pygame.draw.rect(screen, color, rect)
    for x, y in path:
        rect = pygame.Rect(x * (CELL_SIZE + MARGIN), y * (CELL_SIZE + MARGIN), CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, GREEN, rect)
    tx, ty = target_pos
    pygame.draw.rect(screen, RED, pygame.Rect(tx * (CELL_SIZE + MARGIN), ty * (CELL_SIZE + MARGIN), CELL_SIZE, CELL_SIZE))
    dx, dy = drone_pos
    pygame.draw.rect(screen, BLUE, pygame.Rect(dx * (CELL_SIZE + MARGIN), dy * (CELL_SIZE + MARGIN), CELL_SIZE, CELL_SIZE))

    # Draw legend
    legend_items = [("Drone", BLUE), ("Path", GREEN), ("Obstacle", BLACK), ("SOS Strobe", RED)]
    for i, (label, color) in enumerate(legend_items):
        pygame.draw.rect(screen, color, (GRID_SIZE * (CELL_SIZE + MARGIN) + 20, 30 + i * 30, 20, 20))
        text = font.render(label, True, WHITE)
        screen.blit(text, (GRID_SIZE * (CELL_SIZE + MARGIN) + 50, 30 + i * 30))

running = True
sos_found = False
while running:
    clock.tick(FPS)
    draw_grid()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN and not sos_found:
            x, y = drone_pos
            if event.key == pygame.K_w and y > 0 and terrain[y-1][x] == 0:
                drone_pos[1] -= 1
            elif event.key == pygame.K_s and y < GRID_SIZE - 1 and terrain[y+1][x] == 0:
                drone_pos[1] += 1
            elif event.key == pygame.K_a and x > 0 and terrain[y][x-1] == 0:
                drone_pos[0] -= 1
            elif event.key == pygame.K_d and x < GRID_SIZE - 1 and terrain[y][x+1] == 0:
                drone_pos[0] += 1

            if tuple(drone_pos) not in path:
                path.append(tuple(drone_pos))

            if drone_pos == target_pos:
                sos_found = True
                pygame.display.set_caption("✅ SOS Pattern Found!")

pygame.quit()
sys.exit()
