from cmu_graphics import *
import random


class Maze:
    def __init__(self, rows, cols, extra_exits=2):
        self.rows = rows
        self.cols = cols
        self.grid = [[1 for i in range(cols)] for i in range(rows)]
        self.visited = [[False for j in range(cols)] for j in range(rows)]
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
            newRow, newCol = row + dr, col + dc
            # Legality: Stay inside the outer border of walls
            if 1 <= newRow < self.rows - 1 and 1 <= newCol < self.cols - 1:
                if not self.visited[newRow][newCol]:
                    self.grid[row + dr // 2][col + dc // 2] = 0
                    self.generateMaze(newRow, newCol)

    def addExtraExits(self, count):
        # Collect every wall cell on the border next to 0
        edges = []
        for r in range(1, self.rows - 1):
            if self.grid[r][1] == 0: 
                edges.append((r, 0))
            if self.grid[r][self.cols - 2] == 0: 
                edges.append((r, self.cols - 1))
        for c in range(1, self.cols - 1):
            if self.grid[1][c] == 0: 
                edges.append((0, c))
            if self.grid[self.rows - 2][c] == 0: 
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
    def __init__(self, maze):
        self.maze = maze
        self.rows = maze.rows
        self.cols = maze.cols
        self.grid = maze.grid
        self.exits = maze.exits

    def findShortPath(self, start):
        visited = [[False] * self.cols for i in range(self.rows)]
        parent = [[None] * self.cols for j in range(self.rows)]

        path = [start]
        visited[start[0]][start[1]] = True

        while path:
            row, col = path.pop(0)
            if (row, col) in self.exits:
                # Reconstruct the path
                full_path = []
                while (row, col) != start:
                    full_path.append((row, col))
                    row, col = parent[row][col]
                full_path.append(start)
                full_path.reverse()

                # Generate direction to steps mapping
                direction_steps = {'up': [], 'down': [], 'left': [], 'right': []}
                for i in range(1, len(full_path)):
                    r1, c1 = full_path[i - 1]
                    r2, c2 = full_path[i]
                    if r2 == r1 - 1:
                        direction_steps['up'].append(i)
                    elif r2 == r1 + 1:
                        direction_steps['down'].append(i)
                    elif c2 == c1 - 1:
                        direction_steps['left'].append(i)
                    elif c2 == c1 + 1:
                        direction_steps['right'].append(i)

                self.direction_steps = direction_steps  # You can access this from app.pathSolv.direction_steps
                return full_path

            for drow, dcol in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                newRow, newCol = row + drow, col + dcol
                if (0 <= newRow < self.rows and 0 <= newCol < self.cols and
                    self.grid[newRow][newCol] == 0 and 
                    not visited[newRow][newCol]):
                    visited[newRow][newCol] = True
                    parent[newRow][newCol] = (row, col)
                    path.append((newRow, newCol))
        return []

    
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
        possibleDirections = {'up': (-1, 0), 
                              'down': (1, 0), 
                              'left': (0, -1), 
                              'right': (0, 1)}
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
        
        if (targetRow, targetCol) in app.maze.exits:
            onAppStart(app)

        tx = app.boardLeft + targetCol * w + w / 2
        ty = app.boardTop + targetRow * h + h / 2

        if ((dx != 0 and abs(self.x + dx - tx) < self.speed) or
            (dy != 0 and abs(self.y + dy - ty) < self.speed)):
            self.row = targetRow
            self.col = targetCol
            self.updatePixelPosition(app)
            app.shortestPath = app.shortPath.shortestPath((self.row, self.col))
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
    app.shortPath = MazeSolver(app.maze)

    app.showPath = False
    testy = app.shortPath.shortestPath((app.player.row, app.player.col))
    app.shortestPath = testy

    # made quit button with chatGPT
    app.quitButton = {'x': app.width - 150, 
                      'y': app.height - 400,
                      'width': 100, 
                      'height': 40}
    
    # solving maze!
    app.solveButton = {'x': app.width - 150, 
                       'y': app.height - 340,
                       'width': 100,
                       'height': 40}
    app.autoSolve = False
    app.autoPathIndex = 0
    app.autoSolveDelay = 5 
    app.autoSolveCounter = 0
    # solve maze code


# Draw the quit button
def drawQuitButton(app):
    drawRect(app.quitButton['x'], app.quitButton['y'], app.quitButton['width'], 
             app.quitButton['height'], fill='red', border='black')
    drawLabel("Quit", app.quitButton['x'] + app.quitButton['width'] / 2, 
              app.quitButton['y'] + app.quitButton['height'] / 2, 
              font='Arial 16 bold', fill='white')

#solve maze code
def drawSolveButton(app):
    drawRect(app.solveButton['x'], app.solveButton['y'], app.solveButton['width'], 
             app.solveButton['height'], fill='green', border='black')
    drawLabel("Solve", app.solveButton['x'] + app.solveButton['width'] / 2, 
              app.solveButton['y'] + app.solveButton['height'] / 2, 
              font='Arial 16 bold', fill='white')
#solve maze code

# Check if the mouse click is within the quit button area
def onMousePress(app, mouseX, mouseY):
    quitX2 = app.quitButton['x'] + app.quitButton['width']
    quitY2 = app.quitButton['y'] + app.quitButton['height']
    if (app.quitButton['x'] <= mouseX <= quitX2 and
        app.quitButton['y'] <= mouseY <= quitY2):
        app.quit()  
    # Solve button
    solveX2 = app.solveButton['x'] + app.solveButton['width']
    solveY2 = app.solveButton['y'] + app.solveButton['height']
    if (app.solveButton['x'] <= mouseX <= solveX2 and
        app.solveButton['y'] <= mouseY <= solveY2):
        app.autoSolve = True
        app.autoPathIndex = 0

def redrawAll(app):
    drawMazeZoomed(app) 
    drawMaze(app)      
    if app.showPath:
        drawShortestPathMiniMaze(app, 250, 250, 250 / app.rows, 250 / app.cols)
    drawQuitButton(app)
    drawSolveButton(app)

# Full maze at bottom-right (250x250)
def drawMaze(app):
    miniSize = 250
    xOffset = app.width - miniSize
    yOffset = app.height - miniSize
    cellW = miniSize / app.cols
    cellH = miniSize / app.rows

    for row in range(app.rows):
        for col in range(app.cols):
            x = xOffset + col * cellW
            y = yOffset + row * cellH
            # Determine color based on the cell type
            if (row, col) == app.maze.start:
                color = 'lightgreen'
            elif (row, col) in app.maze.exits:
                color = 'gold'
            else:
                color = 'black' if app.maze.grid[row][col] == 1 else 'white'
            drawRect(x,y,cellW,cellH,fill=color,border='gray',borderWidth=1)

    # Player in mini maze
    pr, pc = int(app.player.row), int(app.player.col)
    cx = xOffset + pc * cellW + cellW / 2
    cy = yOffset + pr * cellH + cellH / 2
    drawCircle(cx, cy, min(cellW, cellH) // 3, fill='red')

# Draw the shortest path on the mini maze (smaller than the full maze)
def drawShortestPathMiniMaze(app, xOffset, yOffset, cellW, cellH):
    for (r, c) in app.shortestPath:
        x = xOffset + c * cellW
        y = yOffset + r * cellH
        drawRect(x + 2, y + 2, cellW - 4, cellH - 4, fill=None, 
                 border='red', borderWidth=2)
    # Player in mini maze
    pr, pc = int(app.player.row), int(app.player.col)
    cx = xOffset + pc * cellW + cellW / 2
    cy = yOffset + pr * cellH + cellH / 2
    drawCircle(cx, cy, min(cellW, cellH) // 3, fill='red')

# Zoomed-in 3x3 view on the left half (250x500)
def drawMazeZoomed(app):
    zoomRows, zoomCols = 3, 3
    zoomW = app.width / 2 / zoomCols  
    zoomH = app.height / zoomRows   
    xOffset = 0
    yOffset = 0

    # Find the player’s cell
    playerRow = int(app.player.row)
    playerCol = int(app.player.col)
    
    # Compute top-left cell of the 3x3 zoom based on the player
    startRow = max(0, playerRow - 1)
    startCol = max(0, playerCol - 1)

    for i in range(zoomRows):
        for j in range(zoomCols):
            row = startRow + i
            col = startCol + j
            # Stay in bounds
            if row >= app.rows or col >= app.cols:
                continue
            x = xOffset + j * zoomW
            y = yOffset + i * zoomH
            if (row, col) == app.maze.start:
                color = 'lightgreen'
            elif (row, col) in app.maze.exits:
                color = 'gold'
            else:
                color = 'black' if app.maze.grid[row][col] == 1 else 'white'
            drawRect(x, y, zoomW, zoomH, fill=color, border='gray', 
                     borderWidth=app.cellBorderWidth)

            # Draw red path dot if applicable
            if app.showPath and (row, col) in app.shortestPath:
                drawCircle(x + zoomW/2, y + zoomH/2, min(zoomW, zoomH)//5, 
                           fill='red')
    drawPlayerZoomed(app, startRow, startCol, zoomW, zoomH, xOffset, yOffset)

# Draw player in zoomed view
def drawPlayerZoomed(app, startRow, startCol, zoomW, zoomH, xOffset, yOffset):
    pr, pc = int(app.player.row), int(app.player.col)
    i = pr - startRow
    j = pc - startCol
    if 0 <= i < 3 and 0 <= j < 3:
        cx = xOffset + j * zoomW + zoomW / 2
        cy = yOffset + i * zoomH + zoomH / 2
        r = min(zoomW, zoomH) // 3
        drawCircle(cx, cy, r, fill='red')

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
            app.player.moveDistance = 2 
            return
    app.player.moveDirection = None

def onKeyRelease(app, key):
    # Stop the player when the key is released
    app.player.moveDirection = None
    app.player.moveDistance = 1

def onStep(app):
    app.player.moveStep(app)
    # solve maze code
    if app.autoSolve and app.shortestPath:
        app.autoSolveCounter += 1
        if app.autoSolveCounter >= app.autoSolveDelay:
            app.autoSolveCounter = 0
            if app.autoPathIndex < len(app.shortestPath):
                nextRow, nextCol = app.shortestPath[app.autoPathIndex]
                app.player.row = nextRow
                app.player.col = nextCol
                app.player.updatePixelPosition(app)
                app.autoPathIndex += 1
            else:
                app.autoSolve = False
    #solve maze code

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

