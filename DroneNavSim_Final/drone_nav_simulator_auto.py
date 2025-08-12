
import pygame
import numpy as np
from pathfinding import astar
from terrain_generator import generate_terrain

# Constants
CELL_SIZE = 20
GRID_WIDTH, GRID_HEIGHT = 30, 30
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH + 200
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Autonomous DroneNavSim")

# Terrain and positions
terrain = generate_terrain(GRID_WIDTH, GRID_HEIGHT)
start = (0, 0)
obstacle_coords = np.argwhere(terrain == 1)
for y, x in obstacle_coords:
    terrain[y][x] = 1
free_cells = list(zip(*np.where(terrain == 0)))
goal = start
while goal == start:
    goal = tuple(free_cells[np.random.randint(len(free_cells))])

path = astar(terrain, start, goal)

def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = WHITE
            if terrain[y][x] == 1:
                color = BLACK
            elif (x, y) == goal:
                color = YELLOW
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

    for pos in path:
        if pos != start and pos != goal:
            pygame.draw.rect(screen, GREEN, (pos[0]*CELL_SIZE, pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    pygame.draw.rect(screen, BLUE, (start[0]*CELL_SIZE, start[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_sidebar():
    sidebar_x = GRID_WIDTH * CELL_SIZE
    pygame.draw.rect(screen, GRAY, (sidebar_x, 0, 200, WINDOW_HEIGHT))

    font = pygame.font.SysFont(None, 24)
    legend = [
        ("Drone", BLUE),
        ("Path", GREEN),
        ("Obstacle", BLACK),
        ("SOS Strobe", YELLOW)
    ]
    for i, (label, color) in enumerate(legend):
        y = 20 + i * 30
        pygame.draw.rect(screen, color, (sidebar_x + 20, y, 20, 20))
        text = font.render(label, True, (255, 255, 255))
        screen.blit(text, (sidebar_x + 50, y))

def main():
    draw_grid()
    draw_sidebar()
    pygame.display.flip()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()

if __name__ == "__main__":
    main()
