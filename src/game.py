from cmu_graphics import *
import random

class Player:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.r = radius

    def move(self, direction):
        if direction == 'left' and self.x - self.r > 0:
            self.x -= 5
        elif direction == 'right' and self.x + self.r < 400:
            self.x += 5

    def draw(self):
        drawCircle(self.x, self.y, self.r, fill='lightblue')

    def getBounds(self):
        return (self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 20
        self.h = 10

    def move(self):
        self.y += 5

    def draw(self):
        drawRect(self.x, self.y, self.w, self.h, fill='gold')

    def getBounds(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)

class Hole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 40
        self.h = 20

    def move(self):
        self.y += 5

    def draw(self):
        drawRect(self.x, self.y, self.w, self.h, fill='black')

    def getBounds(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)

class Game:
    def __init__(self, app):
        self.app = app
        self.reset()

    def reset(self):
        self.started = False
        self.over = False
        self.score = 0
        self.player = Player(200, 350, 15)
        self.coins = []
        self.holes = []

    def start(self):
        self.reset()
        self.started = True

    def update(self):
        if not self.started or self.over:
            return

        # Spawn coins and holes
        if random.random() < 0.03:
            self.coins.append(Coin(random.randint(50, 350), 0))
        if random.random() < 0.05:
            self.holes.append(Hole(random.randint(50, 350), 0))

        # Move items
        for coin in self.coins:
            coin.move()
        for hole in self.holes:
            hole.move()

        # Collision detection
        playerBounds = self.player.getBounds()
        self.coins[:] = [c for c in self.coins if not self.checkCollision(playerBounds, c.getBounds()) or self.incrementScore(c)]
        for hole in self.holes:
            if self.checkCollision(playerBounds, hole.getBounds()):
                self.over = True

        # Remove off-screen
        self.coins[:] = [c for c in self.coins if c.y < 400]
        self.holes[:] = [h for h in self.holes if h.y < 400]

    def incrementScore(self, coin):
        self.score += 1
        return False

    def movePlayer(self, direction):
        if self.started and not self.over:
            self.player.move(direction)

    def checkCollision(self, a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)

    def draw(self):
        if not self.started:
            drawLabel('Temple Run', 200, 150, size=40, bold=True)
            drawRect(150, 200, 100, 40, fill='green')
            drawLabel('Start', 200, 220, size=20, fill='white')
        elif self.over:
            drawLabel(f'Game Over! Score: {self.score}', 200, 200, size=30, fill='red', bold=True)
        else:
            self.player.draw()
            for coin in self.coins:
                coin.draw()
            for hole in self.holes:
                hole.draw()
            drawLabel(f'Score: {self.score}', 200, 20, size=18)

def onAppStart(app):
    app.game = Game(app)

def onStep(app):
    app.game.update()

def onKeyHold(app, keys):
    if 'left' in keys:
        app.game.movePlayer('left')
    if 'right' in keys:
        app.game.movePlayer('right')

def onMousePress(app, x, y):
    if not app.game.started:
        if 150 <= x <= 250 and 200 <= y <= 240:
            app.game.start()

def redrawAll(app):
    app.game.draw()

def main():
    runApp()

main()