from cmu_graphics import *
import random

screenWidth = 400
screenHeight = 600
laneOffsets = [-80, 0, 80]

# ---- Perspective Utilities ----
def depth_to_y(depth):
    """Maps depth to vertical screen position"""
    return 100 + 400 * (1 - depth)

def depth_to_scale(depth):
    """Maps depth to scale (size)"""
    return 0.3 + (1 - depth) * 1.2

# ---- Player Class ----
class Player:
    def __init__(self):
        self.lane = 1  # 0 = left, 1 = center, 2 = right
        self.y = 500
        self.color = 'orange'

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1

    def move_right(self):
        if self.lane < 2:
            self.lane += 1

    def draw(self):
        drawRect(200 + laneOffsets[self.lane] - 20, self.y - 20, 40, 40, fill=self.color)

# ---- Obstacle Class ----
class Obstacle:
    def __init__(self, lane, depth=1.0):
        self.lane = lane
        self.depth = depth  # 1.0 is farthest, 0.0 is closest
        self.speed = 0.01  # how fast it comes toward player

    def update(self):
        self.depth -= self.speed

    def draw(self):
        scale = depth_to_scale(self.depth)
        y = depth_to_y(self.depth)
        size = 30 * scale
        x = 200 + laneOffsets[self.lane] * scale
        drawRect(x - size / 2, y - size / 2, size, size, fill='red')

    def is_near_player(self):
        return self.depth < 0.15

# ---- Game Class ----
class Game:
    def __init__(self):
        self.player = Player()
        self.obstacles = []
        self.spawn_timer = 0
        self.game_over = False
        self.score = 0

    def update(self):
        if self.game_over:
            return

        self.spawn_timer += 1
        if self.spawn_timer >= 40:
            lane = random.randint(0, 2)
            self.obstacles.append(Obstacle(lane))
            self.spawn_timer = 0

        for obs in self.obstacles:
            obs.update()

        # Remove passed obstacles
        self.obstacles = [o for o in self.obstacles if o.depth > 0]

        # Collision detection
        for obs in self.obstacles:
            if obs.is_near_player() and obs.lane == self.player.lane:
                self.game_over = True

        self.score += 1

    def draw(self):
        clear('black')

        # Draw road perspective (optional)
        for i in range(20):
            d = i / 20
            y = depth_to_y(d)
            scale = depth_to_scale(d)
            w = 240 * scale
            drawLine(200 - w/2, y, 200 + w/2, y, fill='gray')

        # Draw obstacles
        for obs in sorted(self.obstacles, key=lambda o: o.depth, reverse=True):
            obs.draw()

        # Draw player
        self.player.draw()

        # Score
        drawLabel(f'Score: {self.score}', 10, 10, fill='white', size=16)

        # Game Over
        if self.game_over:
            drawLabel('GAME OVER', 200, 300, size=32, fill='red', align='center')

    def handle_input(self, keys):
        if 'left' in keys:
            self.player.move_left()
        if 'right' in keys:
            self.player.move_right()

# ---- Initialize Game ----
game = Game()

def onStep():
    game.update()

def redrawAll(app):
    game.draw()

def onKeyHold(keys):
    game.handle_input(keys)

cmu_graphics.run()
