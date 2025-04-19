# have the maze generation algorithm

from cmu_graphics import *
import random

# --- NEW CLASS: Maze ---
class Maze:
    def __init__(self, width, height, cell_size):
        self.cols = width // cell_size
        self.rows = height // cell_size
        self.cell_size = cell_size
        self.grid = self.generateMaze()

    def generateMaze(self):
        # Create a winding vertical path from top to bottom
        grid = [['grass' for _ in range(self.cols)] for _ in range(self.rows)]
        col = self.cols // 2  # Start near the center
        for row in range(self.rows):
            grid[row][col] = 'path'
            if random.random() < 0.3:  # Chance to turn left or right
                if col > 1 and random.random() < 0.5:
                    col -= 1
                elif col < self.cols - 2:
                    col += 1
        return grid

    def draw(self, offsetY):
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.cell_size
                y = row * self.cell_size + offsetY
                if 0 <= y < 400:  # Only draw visible part
                    color = 'sienna' if self.grid[row][col] == 'path' else 'darkGreen'
                    drawRect(x, y, self.cell_size, self.cell_size, fill=color, border='black', borderWidth=1)

# --- Sprite Classes ---
class Sprite:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self):
        drawRect(self.x, self.y, self.width, self.height, fill=self.color)

class Player(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20, 'dodgerBlue')
        self.velocity = 5

    def move(self, dx):
        self.x += dx * self.velocity

    def jump(self):
        self.y -= 100

class Coin(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 10, 10, 'gold')

class Hole(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 10, 'black')

# --- Main Game Class ---
class Game:
    def __init__(self):
        self.player = Player(200, 300)
        self.coins = []
        self.holes = []
        self.score = 0
        self.speed = 2
        self.coinTimer = 0
        self.holeTimer = 0

        # --- NEW: Initialize Maze ---
        self.maze = Maze(400, 800, 20)
        self.scrollY = 0

    def update(self):
        # --- NEW: Scroll maze and regenerate when needed ---
        self.scrollY += self.speed
        if self.scrollY >= 20:
            self.scrollY = 0
            self.maze = Maze(400, 800, 20)

        # Move coins and holes down
        for coin in self.coins:
            coin.y += self.speed
        for hole in self.holes:
            hole.y += self.speed

        # Coin spawning
        if self.coinTimer <= 0:
            for row in range(len(self.maze.grid)):
                for col in range(len(self.maze.grid[0])):
                    if self.maze.grid[row][col] == 'path' and random.random() < 0.002:
                        x = col * self.maze.cell_size + self.maze.cell_size // 2
                        y = -row * self.maze.cell_size
                        self.coins.append(Coin(x, y))
            self.coinTimer = 40
        else:
            self.coinTimer -= 1

        # Hole spawning
        if self.holeTimer <= 0:
            for row in range(len(self.maze.grid)):
                for col in range(len(self.maze.grid[0])):
                    if self.maze.grid[row][col] == 'path' and random.random() < 0.001:
                        x = col * self.maze.cell_size
                        y = -row * self.maze.cell_size
                        self.holes.append(Hole(x, y))
            self.holeTimer = 100
        else:
            self.holeTimer -= 1

        # Coin collision
        for coin in self.coins[:]:
            if self.checkCollision(self.player, coin):
                self.coins.remove(coin)
                self.score += 1

        # Hole collision
        for hole in self.holes:
            if self.checkCollision(self.player, hole):
                print("Game Over")
                app.stop()

    def draw(self):
        self.drawRoadBackground()
        self.player.draw()
        for coin in self.coins:
            coin.draw()
        for hole in self.holes:
            hole.draw()
        drawLabel(f"Score: {self.score}", 50, 20, size=16)

    # --- CHANGED: Use maze background instead of plain road ---
    def drawRoadBackground(self):
        self.maze.draw(-self.scrollY)

    def checkCollision(self, sprite1, sprite2):
        return (
            sprite1.x < sprite2.x + sprite2.width and
            sprite1.x + sprite1.width > sprite2.x and
            sprite1.y < sprite2.y + sprite2.height and
            sprite1.y + sprite1.height > sprite2.y
        )

# --- Initialize Game ---
game = Game()

def onStep():
    game.update()

def onKeyHold(key):
    if key == 'left':
        game.player.move(-1)
    elif key == 'right':
        game.player.move(1)
    elif key == 'space':
        game.player.jump()

def onDraw():
    game.draw()


