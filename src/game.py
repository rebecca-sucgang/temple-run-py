from cmu_graphics import *
import random

class Player:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.r = radius

    def move(self, direction):
        if direction == 'left' and self.x - self.r > 100:
            self.x -= 5
        elif direction == 'right' and self.x + self.r < 300:
            self.x += 5

    def draw(self):
        drawCircle(self.x, self.y, self.r, fill='lightblue')

    def getBounds(self):
        return (self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 10

    def move(self):
        self.y += 5

    def draw(self):
        drawCircle(self.x, self.y, self.size, fill='gold')

    def getBounds(self):
        return (self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size)

class Hole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 60
        self.h = 30

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
        self.tutorial = False
        self.over = False
        self.paused = False
        self.score = 0
        self.player = Player(200, 350, 15)
        self.coins = []
        self.hole = None  # Only one hole at a time
        self.coinCooldown = 0

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
        # Generate coins in vertical columns on the road
        if self.coinCooldown <= 0:
            x = random.randint(100, 300)  
            for i in range(5):
                self.coins.append(Coin(x, -i * 25))
            self.coinCooldown = 40
        else:
            self.coinCooldown -= 1

        if self.hole is None and random.random() < 0.03:
            self.hole = Hole(random.randint(120, 240), 0)

        for coin in self.coins:
            coin.move()
        if self.hole:
            self.hole.move()

        playerBounds = self.player.getBounds()

        # Check is player got coins
        updatedCoins = []
        for coin in self.coins:
            if self.checkCollision(playerBounds, coin.getBounds()):
                self.incrementScore(coin)  
            else:
                updatedCoins.append(coin) 

        # Remove coins that have gone off the screen 
        validCoins = []
        for coin in updatedCoins:
            if coin.y < 400: # 400 is screen width 
                validCoins.append(coin)  
        #Adds coin to validCoins list
        self.coins[:] = validCoins  

        # Sprite falls in hole
        if self.hole:
            if self.checkCollision(playerBounds, self.hole.getBounds()):
                self.over = True
            elif self.hole.y > 400:
                self.hole = None

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

    def drawRoadBackground(self):
        drawRect(0, 0, 400, 400, fill='darkGreen')
        # Used ChatGPT to generate road background - after Hack112, I will do it myself
        for y in range(0, 400, 20):
            offset = 10 if (y // 20) % 2 == 0 else 0
            for x in range(100 + offset, 300, 20):
                drawRect(x, y, 20, 20, fill='sienna', border='black', borderWidth=1)

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
            self.drawRoadBackground()
            self.player.draw()
            for coin in self.coins:
                coin.draw()
            if self.hole:
                self.hole.draw()
            drawLabel(f'Score: {self.score}', 200, 20, size=18, bold=True, fill="white")

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
            app.game.reset()

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