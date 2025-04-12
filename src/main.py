from cmu_graphics import *
import random

screenWidth = 400
screenHeight = 600
laneOffsets = [-80, 0, 80]

# ---- Perspective Utilities ----
def depth_to_y(depth):
    return 100 + 400 * (1 - depth)

def depth_to_scale(depth):
    return 0.3 + (1 - depth) * 1.2

# ---- Player Class ----
class Player:
    def __init__(self):
        self.lane = 1
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
        self.depth = depth
        self.speed = 0.01

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

        self.obstacles = [o for o in self.obstacles if o.depth > 0]

        for obs in self.obstacles:
            if obs.is_near_player() and obs.lane == self.player.lane:
                self.game_over = True

        self.score += 1

    def draw(self):
        clear('black')

        for i in range(20):
            d = i / 20
            y = depth_to_y(d)
            scale = depth_to_scale(d)
            w = 240 * scale
            drawLine(200 - w/2, y, 200 + w/2, y, fill='gray')

        for obs in sorted(self.obstacles, key=lambda o: o.depth, reverse=True):
            obs.draw()

        self.player.draw()
        drawLabel(f'Score: {self.score}', 10, 10, fill='white', size=16)

        if self.game_over:
            drawLabel('GAME OVER', 200, 300, size=32, fill='red', align='center')

    def handle_key(self, key):
        if key == 'left':
            self.player.move_left()
        elif key == 'right':
            self.player.move_right()

# ---- App Framework ----
def onAppStart(app):
    app.game = Game()
    app.stepsPerSecond = 60

def onStep(app):
    app.game.update()

def redrawAll(app):
    app.game.draw()

def onKeyHold(app, key):
    app.game.handle_key(key)

def main():
    runApp(width=screenWidth, height=screenHeight)

main()