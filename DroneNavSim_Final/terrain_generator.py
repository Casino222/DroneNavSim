import numpy as np
import random

def generate_terrain(width, height, obstacle_prob=0.2):
    terrain = np.zeros((height, width), dtype=int)
    for y in range(height):
        for x in range(width):
            if random.random() < obstacle_prob:
                terrain[y][x] = 1  # Obstacle
    return terrain