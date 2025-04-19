from cmu_graphics import *
import random
from PIL import Image as PILImage

#------------------- MAZE MODE -------------------#
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

class MazePlayer:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = None
        self.y = None
        self.speed = 2
        self.moveDirection = None

    def updatePixelPosition(self, app):
        w, h = getCellSize(app)
        self.x = app.boardLeft + self.col * w + w / 2
        self.y = app.boardTop + self.row * h + h / 2

    def canMove(self, direction, maze):
        delta = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
        drow, dcol = delta[direction]
        newRow, newCol = self.row + drow, self.col + dcol
        return (0 <= newRow < len(maze.grid) and 0 <= newCol < len(maze.grid[0])
                and maze.grid[newRow][newCol] == 0)

    def moveStep(self, app):
        if not self.moveDirection: return
        if not self.canMove(self.moveDirection, app.maze): return

        w, h = getCellSize(app)
        dx = dy = 0
        if self.moveDirection == 'up': dy = -self.speed
        elif self.moveDirection == 'down': dy = self.speed
        elif self.moveDirection == 'left': dx = -self.speed
        elif self.moveDirection == 'right': dx = self.speed

        targetRow = self.row + (dy != 0) * (1 if dy > 0 else -1)
        targetCol = self.col + (dx != 0) * (1 if dx > 0 else -1)

        tx = app.boardLeft + targetCol * w + w / 2
        ty = app.boardTop + targetRow * h + h / 2

        if ((dx and abs(self.x + dx - tx) < self.speed) or
            (dy and abs(self.y + dy - ty) < self.speed)):
            self.row, self.col = targetRow, targetCol
            self.updatePixelPosition(app)
        else:
            self.x += dx
            self.y += dy

#------------------- NORMAL MODE -------------------#
class Player:
    def __init__(self, x, y, radius): self.x, self.y, self.r = x, y, radius
    def move(self, direction):
        if direction == 'left' and self.x - self.r > 150: self.x -= 5
        elif direction == 'right' and self.x + self.r < 350: self.x += 5
    def draw(self): drawCircle(self.x, self.y, self.r, fill='lightblue')
    def getBounds(self): return (self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)

class Coin:
    def __init__(self, x, y):
        self.x, self.y, self.size = x, y, 20
        self.image = CMUImage(PILImage.open('src/images/classiccoin.png').resize((20, 20)))
    def move(self, speed): self.y += speed
    def draw(self): drawImage(self.image, self.x, self.y)
    def getBounds(self): return (self.x - 20, self.y - 20, self.x + 20, self.y + 20)

class Hole:
    def __init__(self, x, y): self.x, self.y, self.w, self.h = x, y, 60, 30
    def move(self, speed): self.y += speed
    def draw(self): drawRect(self.x, self.y, self.w, self.h, fill='black')
    def getBounds(self): return (self.x, self.y, self.x + self.w, self.y + self.h)

#------------------- APP MANAGEMENT -------------------#
def onAppStart(app):
    app.mode = 'menu'
    app.rows, app.cols = 21, 21
    app.boardLeft, app.boardTop = 50, 50
    app.boardWidth, app.boardHeight = 400, 400
    app.cellBorderWidth = 1

    # Maze Setup
    app.maze = Maze(app.rows, app.cols)
    app.mazePlayer = MazePlayer(*app.maze.start)
    app.mazePlayer.updatePixelPosition(app)

    # Endless Runner Setup
    app.player = Player(200, 350, 15)
    app.coins, app.hole, app.score, app.speed = [], None, 0, 5
    app.coinTimer = 0
    app.roadOffset = 0

def onStep(app):
    if app.mode == 'normal':
        app.speed = 5 + app.score // 10
        app.roadOffset = (app.roadOffset + 2) % 20
        app.coinTimer -= 1
        if app.coinTimer <= 0:
            x = random.randint(150, 350)
            for i in range(5): app.coins.append(Coin(x, -i * 25))
            app.coinTimer = 40
        for coin in app.coins: coin.move(app.speed)
        if app.hole:
            app.hole.move(app.speed)
            if app.hole.y > 500: app.hole = None
        elif random.random() < 0.03:
            app.hole = Hole(random.randint(170, 310), 0)
        app.coins = [c for c in app.coins if c.y < 500 and not checkCollision(app.player.getBounds(), c.getBounds())]
    elif app.mode == 'maze':
        app.mazePlayer.moveStep(app)

def onKeyHold(app, keys):
    if app.mode == 'normal':
        if 'left' in keys: app.player.move('left')
        if 'right' in keys: app.player.move('right')
    elif app.mode == 'maze':
        for d in ['up', 'down', 'left', 'right']:
            if d in keys:
                app.mazePlayer.moveDirection = d
                break
        else:
            app.mazePlayer.moveDirection = None

def onMousePress(app, x, y):
    if app.mode == 'menu':
        if 200 <= x <= 300 and 250 <= y <= 290: app.mode = 'normal'
        elif 200 <= x <= 300 and 310 <= y <= 350: app.mode = 'maze'

def drawMaze(app):
    for r in range(app.rows):
        for c in range(app.cols):
            x, y = getCellLeftTop(app, r, c)
            w, h = getCellSize(app)
            color = 'black' if app.maze.grid[r][c] == 1 else 'white'
            if (r, c) == app.maze.start: color = 'lightgreen'
            elif (r, c) == app.maze.end: color = 'gold'
            drawRect(x, y, w, h, fill=color, border='gray', borderWidth=1)

def redrawAll(app):
    if app.mode == 'menu':
        drawLabel('Choose Game Mode:', 250, 180, size=20, bold=True)
        drawRect(200, 250, 100, 40, fill='lightblue')
        drawLabel('Normal', 250, 270)
        drawRect(200, 310, 100, 40, fill='lightgreen')
        drawLabel('Maze', 250, 330)
    elif app.mode == 'normal':
        drawRect(0, 0, 500, 500, fill='lightyellow')
        for y in range(-40, 500, 20):
            offset = 10 if (y // 20) % 2 == 0 else 0
            for x in range(150 + offset, 350, 20):
                drawRect(x, y + app.roadOffset, 20, 20, fill='sienna', border='black')
        app.player.draw()
        for coin in app.coins: coin.draw()
        if app.hole: app.hole.draw()
        drawLabel(f'Score: {app.score}', 250, 20, size=18, bold=True)
    elif app.mode == 'maze':
        drawMaze(app)
        r = min(getCellSize(app)) // 3
        drawCircle(app.mazePlayer.x, app.mazePlayer.y, r, fill='red')

#------------------- HELPERS -------------------#
def getCellSize(app): return (app.boardWidth / app.cols, app.boardHeight / app.rows)
def getCellLeftTop(app, row, col):
    w, h = getCellSize(app)
    return app.boardLeft + col * w, app.boardTop + row * h
def checkCollision(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)

#------------------- MAIN -------------------#
def main(): runApp(width=500, height=500)
main()
