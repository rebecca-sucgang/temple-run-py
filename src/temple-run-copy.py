
# from cmu_graphics import *

# class Segment:
#     def __init__(self, y, width):
#         self.y = y
#         self.width = width

# class Road:
#     def __init__(self, app, numSegments=50):
#         self.app = app
#         self.segments = []
#         self.numSegments = numSegments
#         self.horizonY = 100
#         self.bottomY = app.height
#         self.speed = 3
#         self.minWidth = 50
#         self.maxWidth = 400
#         self.initSegments()

#     def interpolate(self, start, end, t):
#         return start + (end - start) * t

#     def initSegments(self):
#         for i in range(self.numSegments):
#             self.segments.append(self.createSegment(i))

#     def createSegment(self, index):
#         t = index / self.numSegments
#         y = self.interpolate(self.horizonY, self.bottomY, t)
#         width = self.interpolate(self.minWidth, self.maxWidth, t)
#         return Segment(y, width)

#     def update(self):
#         # Move all segments down
#         for seg in self.segments:
#             seg.y += self.speed

#         # Remove segments off screen
#         self.segments = [seg for seg in self.segments if seg.y < self.app.height]

#         # Add new segment to the top if needed
#         while len(self.segments) < self.numSegments:
#             topSeg = self.segments[0]
#             newY = topSeg.y - self.speed
#             t = (newY - self.horizonY) / (self.bottomY - self.horizonY)
#             newWidth = self.interpolate(self.minWidth, self.maxWidth, t)
#             self.segments.insert(0, Segment(newY, newWidth))

#     def draw(self):
#         # Draw sky background
#         drawRect(0, 0, self.app.width, self.app.height, fill='skyBlue')

#         # Draw road segments as trapezoids
#         for i in range(len(self.segments)-1):
#             seg1 = self.segments[i]
#             seg2 = self.segments[i+1]

#             x1Left = self.app.width / 2 - seg1.width / 2
#             x1Right = self.app.width / 2 + seg1.width / 2
#             x2Left = self.app.width / 2 - seg2.width / 2
#             x2Right = self.app.width / 2 + seg2.width / 2

#             drawPolygon(x1Left, seg1.y,
#                         x1Right, seg1.y,
#                         x2Right, seg2.y,
#                         x2Left, seg2.y,
#                         fill='gray')

# # App functions

# def onAppStart(app):
#     app.road = Road(app)

# def onStep(app):
#     app.road.update()

# def redrawAll(app):
#     app.road.draw()

# def main():
#     runApp(width=400, height=400)

# main()

from cmu_graphics import *
import random

def getRoadBounds(y, screen_width=400, screen_height=400): #this is AI
    t = y / screen_height
    left  = 150 * (1 - t)
    right = 250 + 150 * t  # right = 400 - left
    return left, right

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
        # propose new X (this is suggested by AI)
        dx = -5 if direction=='left' else (5 if direction=='right' else 0)
        newX = self.x + dx
        # clamp within the road at this player's Y (AI also)
        left, right = getRoadBounds(self.y)
        minX = left  + self.r
        maxX = right - self.r
        self.x = max(minX, min(newX, maxX))

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

class RoadLine:
    def __init__(self, y):
        self.y = y
        self.width = 10 + y // 10

    def move(self):
        self.y += 5
        if self.y > 400:
            self.y = 0
            self.width = 10
        else:
            self.width = min(80, self.width + 1)

    def draw(self):
        x = 200
        h = 20
        drawRect(x - self.width / 2, self.y, self.width, h, fill='white')

class Game:
    def __init__(self, app):
        self.app = app
        self.reset()

    def reset(self):
        self.started = False
        self.over = False
        self.tutorial = False
        self.paused = False
        self.score = 0
        self.player = Player(200, 350, 15)
        self.coins = []
        self.holes = []
        self.roadLines = [RoadLine(i * 60) for i in range(10)]

    def start(self):
        self.reset()
        self.started = True

    def instructions(self):
        if not self.started:
            self.tutorial = True

    def togglePause(self):
        if self.started and not self.over:
            self.paused = not self.paused

    def update(self):
        if not self.started or self.over or self.paused:
            return

        # Update road lines
        for line in self.roadLines:
            line.move()

        # Spawn coins and holes (AI)
        left0, right0 = getRoadBounds(0)
        if random.random() < 0.03:
            spawnX = random.uniform(left0, right0 - Coin(0,0).w)
            self.coins.append(Coin(spawnX, 0))
        if random.random() < 0.05:
            spawnX = random.uniform(left0, right0 - Hole(0,0).w)
            self.holes.append(Hole(spawnX, 0))

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
        if self.tutorial:
            drawLabel('How to Play', 200, 80, size=30, bold=True)
            drawLabel('Move Left: Press the ← key', 200, 140, size=20)
            drawLabel('Move Right: Press the → key', 200, 180, size=20)
            drawLabel('Avoid the obstacles.', 200, 220, size=20)
            drawLabel('Collect the gold coins.', 200, 260, size=20)
            drawLabel('Press P to pause.', 200, 300, size=20)

            drawRect(150, 340, 100, 40, fill='gray')
            drawLabel('Back', 200, 360, size=20, fill='white')
        elif not self.started:
            drawLabel('Temple Run', 200, 150, size=40, bold=True)
            drawRect(150, 200, 100, 40, fill='green')
            drawLabel('Start', 200, 220, size=20, fill='white')
            
            drawRect(150, 260, 100, 40, fill='orange')
            drawLabel('How to Play', 200, 280, size=15, fill='white')
        elif self.paused:
            drawLabel('Paused', 200, 200, size=20, fill='orange', bold=True)
        elif self.over:
            drawLabel(f'Game Over! Score: {self.score}', 200, 200, size=30, fill='red', bold=True)

            drawRect(150, 340, 100, 40, fill='gray')
            drawLabel('Start over', 200, 360, size=20, fill='white')
        else:
            # Draw road base
            drawPolygon(150, 0, 250, 0, 400, 400, 0, 400, fill='gray')

            # Draw road lines
            for line in self.roadLines:
                line.draw()

            # Draw objects
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

def onKeyPress(app, key):
    if key == 'p':
        app.game.togglePause()

def onMousePress(app, x, y):
    if app.game.tutorial:
        if 150 <= x <= 250 and 340 <= y <= 380:
            # Return to main menu
            app.game.tutorial = False
    
    elif app.game.over:
        if 150 <= x <= 250 and 340 <= y <= 380:
            # Return to main menu
            app.game.started = not app.game.started

    elif not app.game.started:
        if 150 <= x <= 250 and 200 <= y <= 240:
            app.game.start()

        elif 150 <= x <= 250 and 260 <= y <= 300:
            app.game.instructions()

def redrawAll(app):
    app.game.draw()

def main():
    runApp()

main()