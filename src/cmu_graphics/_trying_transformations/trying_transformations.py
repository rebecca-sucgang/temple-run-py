pip install pygame
import numpy

def iso_projection(x, y, z=0):
    """Convert 3D (x, y, z) to 2D isometric (screen_x, screen_y)"""
    screen_x = (x - y) * 64
    screen_y = (x + y) * 32 - z * 32
    return int(screen_x), int(screen_y)

pygame.draw.polygon()