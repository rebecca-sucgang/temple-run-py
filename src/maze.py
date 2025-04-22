from cmu_graphics import *
import random


class Maze:
    def __init__(self, rows, cols, extra_exits=2):
        self.rows = rows
        self.cols = cols
        self.grid = [[1 for _ in range(cols)] for _ in range(rows)]
        self.visited = [[False for _ in range(cols)] for _ in range(rows)]
        self.start = (1, 1)
        self.end = (rows - 2, cols - 2)
        self.exits = [self.end]

        self.generateMaze(*self.start)
        self.addExtraExits(extra_exits)

    def generateMaze(self, row, col):
        # Mark the current cell as visited and carve a passage (0 = open space)
        self.visited[row][col] = True
        self.grid[row][col] = 0

        #possible directions
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions) # Randomize for a organic maze

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            # Legality: Stay inside the outer border of walls (index 0 and last index stay solid)
            if 1 <= new_row < self.rows - 1 and 1 <= new_col < self.cols - 1:
                if not self.visited[new_row][new_col]:
                    self.grid[row + dr // 2][col + dc // 2] = 0
                    self.generateMaze(new_row, new_col)

    def addExtraExits(self, count):
        # Collect every wall cell on the border that sits next to an interior path (0)
        edges = []
        for r in range(1, self.rows - 1):
            if self.grid[r][1] == 0: # possible left border candidate 
                edges.append((r, 0))
            if self.grid[r][self.cols - 2] == 0: # possible right border condidate
                edges.append((r, self.cols - 1))
        for c in range(1, self.cols - 1):
            if self.grid[1][c] == 0: # possible top border candidate
                edges.append((0, c))
            if self.grid[self.rows - 2][c] == 0: # possible bottom border candidate
                edges.append((self.rows - 1, c))

        random.shuffle(edges) # to randomize the exits we open up
        for _ in range(min(count, len(edges))):
            r, c = edges.pop()
            self.grid[r][c] = 0 # carves the exit
            self.exits.append((r, c)) # tracks the exit

    def isPath(self, row, col):
        # helper: true if the cell is open basically
        return self.grid[row][col] == 0

class MazeSolver:
    def __init__(self, maze, start=None):
        self.maze = maze
        self.rows = maze.rows
        self.cols = maze.cols
        self.grid = maze.grid
        self.start = start if start else maze.start  # using player's position if provided
        self.exits = maze.exits

    def findShortestPath(self):
        start = self.start
        visited = [[False] * self.cols for _ in range(self.rows)]
        parent = [[None] * self.cols for _ in range(self.rows)]

        # Breadth‑first search (BFS) queue; list with pop(0) ≈ deque.popleft()
        path = []
        path.append(start)
        visited[start[0]][start[1]] = True

        while path:
            row, col = path.pop(0)  # Simulating popleft() using pop(0)
            # Exit found → backtrack to reconstruct path
            if (row, col) in self.exits:
                path = []
                while (row, col) != start:
                    path.append((row, col))
                    row, col = parent[row][col]
                path.append(start)
                path.reverse()
                return path  # Shortest path (BFS guarantees minimal steps)
            
            # Explores 4‑neighbour cells
            for drow, dcol in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_row, new_col = row + drow, col + dcol
                if (0 <= new_row < self.rows and 0 <= new_col < self.cols and
                    self.grid[new_row][new_col] == 0 and not visited[new_row][new_col]):
                    visited[new_row][new_col] = True
                    parent[new_row][new_col] = (row, col)
                    path.append((new_row, new_col))
        return [] # like return None -> no path is reachable from the start


class MazePlayer:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = None
        self.y = None
        self.speed = 2
        self.moveDirection = None
        self.facing = 'up'

    def updatePixelPosition(self, app):
        w, h = getCellSize(app)
        self.x = app.boardLeft + self.col * w + w / 2
        self.y = app.boardTop + self.row * h + h / 2

    def canMove(self, direction, maze):
        possibleDirections = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
        drow, dcol = possibleDirections[direction]
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
        if self.moveDirection == 'up': dy = -self.speed
        elif self.moveDirection == 'down': dy = self.speed
        elif self.moveDirection == 'left': dx = -self.speed
        elif self.moveDirection == 'right': dx = self.speed

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

    app.maze = Maze(app.rows, app.cols, extra_exits=3)
    app.player = MazePlayer(*app.maze.start)
    app.player.updatePixelPosition(app)
    app.shortestPathSolver = MazeSolver(app.maze, start=(app.player.row, app.player.col))

    app.showPath = False
    app.shortestPath = app.shortestPathSolver.findShortestPath()

def redrawAll(app):
    drawLabel('Maze Game (arrow keys to move, r = reset, p = path)', 250, 30, size=14)
    drawMaze(app)
    if app.showPath:
        drawShortestPath(app)
    drawPlayer(app)

def drawMaze(app):
    for row in range(app.rows):
        for col in range(app.cols):
            x, y = getCellLeftTop(app, row, col)
            w, h = getCellSize(app)
            if (row, col) == app.maze.start:
                color = 'lightgreen'
            elif (row, col) in app.maze.exits:
                color = 'gold'
            else:
                color = 'black' if app.maze.grid[row][col] == 1 else 'white'
            drawRect(x, y, w, h, fill=color, border='gray', borderWidth=app.cellBorderWidth)

def drawPlayer(app):
    r = min(getCellSize(app)) // 3
    drawCircle(app.player.x, app.player.y, r, fill='red')

def drawShortestPath(app):
    for (r, c) in app.shortestPath:
        x, y = getCellLeftTop(app, r, c)
        w, h = getCellSize(app)
        drawRect(x+2, y+2, w-4, h-4, fill=None, border='red', borderWidth=2)

def onKeyPress(app, key):
    if key == 'r':
        onAppStart(app)
    elif key == 'p':
        app.showPath = not app.showPath

def onKeyHold(app, keys):
    for direction in ['up', 'down', 'left', 'right']:
        if direction in keys:
            app.player.moveDirection = direction
            return
    app.player.moveDirection = None

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
