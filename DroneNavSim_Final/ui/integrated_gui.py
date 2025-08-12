
import pygame
import sys
import os
import numpy as np
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pathfinding import astar
from terrain_generator import generate_terrain
from sos_detector import detect_sos_pattern

# Constants
TILE_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
WINDOW_WIDTH = TILE_SIZE * GRID_WIDTH + 200
WINDOW_HEIGHT = TILE_SIZE * GRID_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (160, 160, 160)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

class DroneSimulator:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Integrated DroneNavSim")
        self.clock = pygame.time.Clock()
        self.reset_simulation()

    def reset_simulation(self):
        self.terrain = generate_terrain(GRID_WIDTH, GRID_HEIGHT, obstacle_prob=0.25)
        self.start = (0, 0)
        self.goal = (np.random.randint(5, GRID_WIDTH), np.random.randint(5, GRID_HEIGHT))
        while self.terrain[self.goal[1]][self.goal[0]] == 1:
            self.goal = (np.random.randint(5, GRID_WIDTH), np.random.randint(5, GRID_HEIGHT))
        self.strobe_pos = self.goal
        self.path = astar(self.terrain, self.start, self.goal)
        self.path_index = 0
        self.last_move_time = time.time()
        self.drone_pos = self.start
        self.detected_sos = False

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = WHITE
                if self.terrain[y][x] == 1:
                    color = BLACK
                elif (x, y) == self.drone_pos:
                    color = BLUE
                elif (x, y) == self.strobe_pos:
                    color = YELLOW
                elif (x, y) in self.path[:self.path_index]:
                    color = GREEN
                pygame.draw.rect(self.window, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE - 1, TILE_SIZE - 1))

    def draw_legend(self):
        font = pygame.font.SysFont(None, 24)
        labels = [
            (BLUE, "Drone"),
            (GREEN, "Path"), 
            (BLACK, "Obstacle"),
            (YELLOW, "SOS Strobe"),
        ]
        for i, (color, text) in enumerate(labels):
            pygame.draw.rect(self.window, color, (GRID_WIDTH * TILE_SIZE + 20, 30 + i * 30, 20, 20))
            label = font.render(text, True, WHITE)
            self.window.blit(label, (GRID_WIDTH * TILE_SIZE + 50, 30 + i * 30))

        if self.detected_sos:
            msg = font.render("✅ SOS Detected!", True, GREEN)
            self.window.blit(msg, (GRID_WIDTH * TILE_SIZE + 20, 200))

    def update_autonomous(self):
        now = time.time()
        if self.path_index < len(self.path) and now - self.last_move_time > 0.3:
            self.drone_pos = self.path[self.path_index]
            self.path_index += 1
            self.last_move_time = now

        if self.drone_pos == self.strobe_pos and not self.detected_sos:
            result = detect_sos_pattern()
            self.detected_sos = result

    def run(self):
        running = True
        while running:
            self.window.fill(GRAY)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_simulation()
                    elif event.key == pygame.K_q:
                        running = False

            self.update_autonomous()
            self.draw_grid()
            self.draw_legend()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sim = DroneSimulator()
    sim.run()
