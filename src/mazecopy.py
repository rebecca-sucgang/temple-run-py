from cmu_graphics import *
from PIL import Image as PILImage
from ui_assets import UIButton, UIMazeBlock
import random

class Maze:
    def __init__(self, rows, cols, extra_exits=2):
        self.rows = rows
        self.cols = cols
        self.grid = [[1 for j in range(cols)] for _ in range(rows)]
        self.visited = [[False for i in range(cols)] for _ in range(rows)]
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
            # Legality Check: Stay inside the outer border of walls
            if 1 <= newRow < self.rows - 1 and 1 <= newCol < self.cols - 1:
                if not self.visited[newRow][newCol]:
                    self.grid[row + dr // 2][col + dc // 2] = 0
                    self.generateMaze(newRow, newCol)

    def addExtraExits(self, count):
        # Collect every wall cell on the border that sits next to (0)
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

        # Inspired by (BFS): https://www.youtube.com/watch?v=W9F8fDQj7Ok&t=217s
        path = [start]
        visited[start[0]][start[1]] = True

        while path:
            row, col = path.pop(0)
            if (row, col) in self.exits:
                path = []
                while (row, col) != start:
                    path.append((row, col))
                    row, col = parent[row][col]
                path.append(start)
                path.reverse()
                return path

            for drow, dcol in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                newRow, newCol = row + drow, col + dcol
                if (0 <= newRow < self.rows and 0 <= newCol < self.cols and
                    self.grid[newRow][newCol] == 0 and 
                    not visited[newRow][newCol]):
                    visited[newRow][newCol] = True
                    parent[newRow][newCol] = (row, col)
                    path.append((newRow, newCol))
        return []  # No path found
    
class MazePlayer:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = None
        self.y = None
        self.speed = 2
        self.moveDirection = None
        self.facing = 'down'

        # asked help from chatgpt on how to include sprites
        self.frameIndex = 0
        self.tick = 0
        self.frameCount = 5
        self.frameWidth = 50
        self.frameHeight = 50
        self.zoomDisplaySize = 45
        self.miniDisplaySize = 10

        self.sprites = {
            'up': PILImage.open('src/images/sprites/runup-removebg.png'),
            'down': PILImage.open('src/images/sprites/rundown-removebg.png'),
            'left': PILImage.open('src/images/sprites/runleft-removebg.png'),
            'right': PILImage.open('src/images/sprites/runright-removebg.png'),
        }   

    def getCurrentFrame(self, displaySize): # asked ChatGPT for help
        spriteSheet = self.sprites[self.facing] # which direction in dictionary
        left = self.frameIndex * self.frameWidth
        top = 0
        cropped = spriteSheet.crop((left, top, left + self.frameWidth, self.frameHeight))
        resized = cropped.resize((displaySize, displaySize))
        return CMUImage(resized)

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
        
        self.facing = self.moveDirection  # Update facing direction
        self.tick += 1
        if self.tick % 5 == 0:
            self.frameIndex = (self.frameIndex + 1) % self.frameCount
        
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
            app.mazesSolved += 1
            app.mazeGame.__init__(app) # fixed this bug using ChatGPT
            return

        tx = app.boardLeft + targetCol * w + w / 2
        ty = app.boardTop + targetRow * h + h / 2

        if ((dx != 0 and abs(self.x + dx - tx) < self.speed) or
            (dy != 0 and abs(self.y + dy - ty) < self.speed)):
            self.row = targetRow
            self.col = targetCol
            self.updatePixelPosition(app)
            app.shortPath = app.pathSolv.findShortPath((self.row, self.col))
        else:
            self.x += dx
            self.y += dy

def getCellSize(app):
    return (app.boardWidth / app.cols, app.boardHeight / app.rows)

def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    return app.boardLeft + col * cellWidth, app.boardTop + row * cellHeight

def getCellCenter(app, row, col):
    x, y = getCellLeftTop(app, row, col)
    w, h = getCellSize(app)
    return x + w/2, y + h/2

# overall citation for following code: ChatGPT helped me to just organize the code into
#  a new MazeGame class in order to link this maze mode to game.py
class MazeGame:
    def __init__(self, app):
        app.rows = 21
        app.cols = 21
        app.boardLeft = 50
        app.boardTop = 50
        app.boardWidth = 400
        app.boardHeight = 400
        app.cellBorderWidth = 1

        # Citation: ChatGPT after debugging app.mazesSolved problem
        app.mazesSolved = getattr(app, 'mazesSolved', 0)

        app.maze = Maze(app.rows, app.cols, extra_exits=3)
        app.player = MazePlayer(*app.maze.start)
        app.player.updatePixelPosition(app)
        app.pathSolv = MazeSolver(app.maze)

        app.autoSolve = False
        app.shortestPath = app.pathSolv.findShortPath((app.player.row, app.player.col))
        app.autoPathIndex = 0
        app.autoSolveDelay = 5
        app.autoSolveCounter = 0

        app.showPath = False
        app.shortPath = app.pathSolv.findShortPath((app.player.row, app.player.col))

        # Citation: made quit button with chatGPT
        app.quitButton = {'x': app.width - 150, 
                          'y': app.height - 400, 
                          'width': 100, 
                          'height': 40}
        app.solveButton = {'x': app.width - 150, 
                    'y': app.height - 340,
                    'width': 100,
                    'height': 40}
        self.UIButton = UIButton()
        self.UIMazeBlock = UIMazeBlock()

    def onStep(self, app):
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

    def onKeyPress(self, app, key):
        if key == 'r':
            self.__init__(app)
        elif key == '?':
            app.showPath = not app.showPath

    def onKeyHold(self, app, keys):
        for direction in ['up', 'down', 'left', 'right']:
            if direction in keys:
                app.player.moveDirection = direction
                app.player.moveDistance = 2
                return
        app.player.moveDirection = None

    def onKeyRelease(self, app, key):
        # Stop the player when the key is released
        app.player.moveDirection = None
        app.player.moveDistance = 1

    # Check if the mouse click is within the quit button area
    def onMousePress(self, app, x, y):
        bx = app.quitButton['x'] + app.quitButton['width']
        by = app.quitButton['y'] + app.quitButton['height']
        if (app.quitButton['x'] <= x <= bx and app.quitButton['y'] <= y <= by):
            app.gameMode = 'main'
        # Solve button
        solveX2 = app.solveButton['x'] + app.solveButton['width']
        solveY2 = app.solveButton['y'] + app.solveButton['height']
        if (app.solveButton['x'] <= x <= solveX2 and
            app.solveButton['y'] <= y <= solveY2):
            app.autoSolve = True
            app.autoPathIndex = 0

    def redrawAll(self, app):
        self.drawMazeZoomed(app)
        self.drawMaze(app)
        if app.showPath:
            self.drawShortestPathMiniMaze(app, 250, 250, 250 / app.rows, 250 / app.cols)
        self.drawQuitButton(app)
        self.drawSolveButton(app)
        drawLabel(f"Amount of Mazes Solved: {app.mazesSolved}", 375, 50, fill="black", size=15, bold=True)

    # Draw the quit button
    def drawQuitButton(self, app):
        drawRect(app.quitButton['x'], app.quitButton['y'], app.quitButton['width'], app.quitButton['height'], fill='red', border='sienna', borderWidth=2)
        drawLabel("Quit", app.quitButton['x'] + app.quitButton['width'] / 2, app.quitButton['y'] + app.quitButton['height'] / 2, font='Arial 16 bold', fill='beige')

    #solve maze code
    def drawSolveButton(self, app):
        drawRect(app.solveButton['x'], app.solveButton['y'], app.solveButton['width'], 
                app.solveButton['height'], fill='green', border='black')
        drawLabel("Solve", app.solveButton['x'] + app.solveButton['width'] / 2, 
                app.solveButton['y'] + app.solveButton['height'] / 2, 
                font='Arial 16 bold', fill='white')
    #solve maze code

    # Full maze at bottom-right (250x250)
    def drawMaze(self, app):
        miniSize = 250
        xOffset = app.width - miniSize
        yOffset = app.height - miniSize
        cellW = miniSize / app.cols
        cellH = miniSize / app.rows
        for row in range(app.rows):
            for col in range(app.cols):
                x = xOffset + col * cellW
                y = yOffset + row * cellH
                if (row, col) in app.maze.exits:
                    drawImage(self.UIMazeBlock.mazeEndImage, x, y, width=cellW, height=cellH)
                elif app.maze.grid[row][col] == 1:
                    drawImage(self.UIMazeBlock.mazeBorderImage, x, y, width=cellW, height=cellH)
                else:
                    drawImage(self.UIMazeBlock.mazePathImage, x, y, width=cellW, height=cellH)
        
        # Player in mini maze
        pr, pc = int(app.player.row), int(app.player.col)
        cx = xOffset + pc * cellW + cellW / 2
        cy = yOffset + pr * cellH + cellH / 2
        frame = app.player.getCurrentFrame(app.player.miniDisplaySize)
        drawImage(frame, cx - app.player.miniDisplaySize // 2, cy - app.player.miniDisplaySize // 2)

    # Zoomed-in 3x3 view on the left half (250x500)
    def drawMazeZoomed(self, app):
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
                if row >= app.rows or col >= app.cols:
                    continue
                x = xOffset + j * zoomW
                y = yOffset + i * zoomH
                if (row, col) in app.maze.exits:
                    drawImage(self.UIMazeBlock.mazeEndImage, x, y, width=zoomW, height=zoomH)
                elif app.maze.grid[row][col] == 1:
                    drawImage(self.UIMazeBlock.mazeBorderImage, x, y, width=zoomW, height=zoomH)
                else:
                    drawImage(self.UIMazeBlock.mazePathImage, x, y, width=zoomW, height=zoomH)

                # Draw red path dot if applicable
                if app.showPath and (row, col) in app.shortPath:
                    drawCircle(x + zoomW/2, y + zoomH/2, min(zoomW, zoomH)//5, fill='red')
        self.drawPlayerZoomed(app, startRow, startCol, zoomW, zoomH, xOffset, yOffset)

    # Draw player in zoomed view
    def drawPlayerZoomed(self, app, startRow, startCol, zoomW, zoomH, xOffset, yOffset):
        pr, pc = int(app.player.row), int(app.player.col)
        i = pr - startRow
        j = pc - startCol
        if 0 <= i < 3 and 0 <= j < 3:
            frame = app.player.getCurrentFrame(app.player.zoomDisplaySize)
            drawImage(frame, xOffset + j * zoomW + (zoomW - app.player.zoomDisplaySize) // 2, yOffset + i * zoomH + (zoomH - app.player.zoomDisplaySize) // 2)

    # Draw the shortest path on the mini maze 
    def drawShortestPathMiniMaze(self, app, xOffset, yOffset, cellW, cellH):
        for (r, c) in app.shortPath:
            x = xOffset + c * cellW
            y = yOffset + r * cellH
            drawRect(x + 2, y + 2, cellW - 4, cellH - 4, fill=None, border='red', borderWidth=2)