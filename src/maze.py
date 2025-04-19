from cmu_graphics import *
import random

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
        
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]  # Up, Down, Right, Left
        random.shuffle(directions)  # Randomize directions to ensure random maze generation
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            # Check if the new row and column are within bounds
            if 1 <= new_row < self.rows - 1 and 1 <= new_col < self.cols - 1:
                if not self.visited[new_row][new_col]:
                    # Carve a path by setting the cell between current and new position to 0
                    self.grid[row + dr // 2][col + dc // 2] = 0
                    # Recursively generate maze from the new cell
                    self.generateMaze(new_row, new_col)

    def isPath(self, row, col):
        return self.grid[row][col] == 0


class Player:
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
        delta = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
        drow, dcol = delta[direction]
        newRow = self.row + drow
        newCol = self.col + dcol

        if (0 <= newRow < len(maze.grid) and 
            0 <= newCol < len(maze.grid[0]) and 
            maze.grid[newRow][newCol] == 0):
            return True
        return False

    def moveStep(self, app):
        if not self.moveDirection: return

        w, h = getCellSize(app)
        dx = dy = 0
        if self.moveDirection == 'up':
            dy = -self.speed
        elif self.moveDirection == 'down':
            dy = self.speed
        elif self.moveDirection == 'left':
            dx = -self.speed
        elif self.moveDirection == 'right':
            dx = self.speed

        # Distance to center of next cell
        targetRow = self.row
        targetCol = self.col
        if self.moveDirection == 'up': targetRow -= 1
        if self.moveDirection == 'down': targetRow += 1
        if self.moveDirection == 'left': targetCol -= 1
        if self.moveDirection == 'right': targetCol += 1

        if not self.canMove(self.moveDirection, app.maze):
            return

        tx = app.boardLeft + targetCol * w + w / 2
        ty = app.boardTop + targetRow * h + h / 2

        if ((dx != 0 and abs(self.x + dx - tx) < self.speed) or
            (dy != 0 and abs(self.y + dy - ty) < self.speed)):
            self.row = targetRow
            self.col = targetCol
            self.updatePixelPosition(app)
        else:
            self.x += dx
            self.y += dy

def onAppStart(app):
    app.rows = 21
    app.cols = 21
    app.boardLeft = 50
    app.boardTop = 50
    app.boardWidth = 400
    app.boardHeight = 400
    app.cellBorderWidth = 1

    app.maze = Maze(app.rows, app.cols)
    app.player = Player(*app.maze.start)
    app.player.updatePixelPosition(app)

def redrawAll(app):
    drawLabel('Maze Game (Arrow keys to move, r to regenerate)', 250, 30, size=16)
    drawMaze(app)
    drawPlayer(app)

def drawMaze(app):
    for row in range(app.rows):
        for col in range(app.cols):
            x, y = getCellLeftTop(app, row, col)
            w, h = getCellSize(app)

            if (row, col) == app.maze.start:
                color = 'lightgreen'
            elif (row, col) == app.maze.end:
                color = 'gold'
            else:
                color = 'black' if app.maze.grid[row][col] == 1 else 'white'

            drawRect(x, y, w, h, fill=color, border='gray', borderWidth=app.cellBorderWidth)

def drawPlayer(app):
    r = min(getCellSize(app)) // 3
    drawCircle(app.player.x, app.player.y, r, fill='red')

def onKeyPress(app, key):
    if key == 'r':
        onAppStart(app)

def onKeyHold(app, keys):
    for direction in ['up', 'down', 'left', 'right']:
        if direction in keys:
            app.player.moveDirection = direction
            return
    app.player.moveDirection = None

#---------------------- Smooth Movement ----------------------#

def onStep(app):
    app.player.moveStep(app)

def getCellSize(app):
    return (app.boardWidth / app.cols, app.boardHeight / app.rows)

def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    return app.boardLeft + col * cellWidth, app.boardTop + row * cellHeight

def getCellCenter(app, row, col):
    x, y = getCellLeftTop(app, row, col)
    w, h = getCellSize(app)
    return x + w/2, y + h/2

def main():
    runApp(width=500, height=500)

main()
