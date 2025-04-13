from cmu_graphics import *
import pygame
import random

# --- Game Setup ---
pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 165, 0))
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT - 60))

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += 5

# --- Obstacle Class ---
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((200, 0, 0))
        self.rect = self.image.get_rect(center=(random.choice([100, 200, 300]), -40))

    def update(self):
        self.rect.y += 6
        if self.rect.top > HEIGHT:
            self.kill()

# --- Main Game Loop ---
player = Player()
player_group = pygame.sprite.Group(player)
obstacles = pygame.sprite.Group()

score = 0
running = True
spawn_timer = 0

while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update(keys)

    spawn_timer += 1
    if spawn_timer > 40:
        obstacles.add(Obstacle())
        spawn_timer = 0

    obstacles.update()

    # Collision detection
    if pygame.sprite.spritecollideany(player, obstacles):
        print("Game Over!")
        running = False

    screen.fill((0, 0, 0))
    player_group.draw(screen)
    obstacles.draw(screen)
    pygame.display.flip()

pygame.quit()