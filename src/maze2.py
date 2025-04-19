from cmu_graphics import *
import random
from PIL import Image as PILImage

class Player:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.direction = 'up'  # 'up', 'down', 'left', 'right'

        # Load player sprite (assuming a sprite for movement is available)
        spriteSheet = PILImage.open('src/images/player_sprite.png')
        frameCount = 4  # Assume 4 frames for animation (one for each direction)
        frameWidth = spriteSheet.width // frameCount
        frameHeight = spriteSheet.height

        self.sprites = []
        self.spriteIndex = 0
        self.spriteTimer = 0

        # Crop and resize sprite frames
        for i in range(frameCount):
            frame = spriteSheet.crop((i * frameWidth, 0, (i + 1) * frameWidth, frameHeight))
            resizedFrame = frame.resize((40, 60))  # Adjust size for player sprite
            self.sprites.append(CMUImage(resizedFrame))

    def rotateLeft(self):
        dirs = ['up', 'left', 'down', 'right']
        self.direction = dirs[(dirs.index(self.direction) + 1) % 4]

    def rotateRight(self):
        dirs = ['up', 'right', 'down', 'left']
        self.direction = dirs[(dirs.index(self.direction) + 1) % 4]

    def move(self, maze):
        d = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
        dr, dc = d[self.direction]
        newR = self.y + dr
        newC = self.x + dc
        if 0 <= newR < maze.rows and 0 <= newC < maze.cols:
            if maze.grid[newR][newC] == 0:
                self.x, self.y = newC, newR

    def draw(self):
        if self.direction:
            self.spriteTimer += 1
            if self.spriteTimer >= 4:  # Lower -> faster animation
                self.spriteIndex = (self.spriteIndex + 1) % len(self.sprites)
                self.spriteTimer = 0
        else:
            self.spriteIndex = 0
        
        drawImage(self.sprites[self.spriteIndex], self.x * 20, self.y * 20)

class Maze:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[1 for _ in range(cols)] for _ in range(rows)]
        self.visited = [[False for _ in range(cols)] for _ in range(rows)]
        self.start = (1, 1)
        self.end = (rows - 2, cols - 2)
        self.generateMaze(*self.start)

    def generateMaze(self, row, col):
        self.visited[row][col] = True
        self.grid[row][col] = 0
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 1 <= new_row < self.rows - 1 and 1 <= new_col < self.cols - 1:
                if not self.visited[new_row][new_col]:
                    self.grid[row + dr // 2][col + dc // 2] = 0
                    self.generateMaze(new_row, new_col)

def onAppStart(app):
    app.rows = 21
    app.cols = 21
    app.maze = Maze(app.rows, app.cols)
    app.player = Player(1, 1, 15)

def redrawAll(app):
    drawRect(0, 0, 500, 500, fill='darkGreen')
    drawLabel('Maze Game (WASD + R)', 250, 20, size=14)
    drawMazeView(app)

def drawMazeView(app):
    # Draw maze walls and the player in 2D perspective
    for row in range(app.maze.rows):
        for col in range(app.maze.cols):
            if app.maze.grid[row][col] == 1:
                drawRect(col * 20, row * 20, 20, 20, fill='black')

    app.player.draw()

def onKeyPress(app, key):
    if key == 'r':
        onAppStart(app)
    elif key == 'a':
        app.player.rotateLeft()
    elif key == 'd':
        app.player.rotateRight()
    elif key == 'w':
        app.player.move(app.maze)
    elif key == 's':
        app.player.move(app.maze)

def main():
    runApp(width=500, height=500)

main()
