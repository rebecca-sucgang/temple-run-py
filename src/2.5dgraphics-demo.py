# demoing ursina 

from cmu_graphics import *
from ursina import *
import random

class Cube:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frontPoints = [
            (100, 100),  # Front top-left
            (200, 100),  # Front top-right
            (200, 200),  # Front bottom-right
            (100, 200)   # Front bottom-left
        ]
        self.backPoints = [
            (120, 120),  # Back top-left
            (220, 120),  # Back top-right
            (220, 220),  # Back bottom-right
            (120, 220)   # Back bottom-left
        ]
    
    def draw(self):
        # Draw the front square
        drawPolygon(self.frontPoints, fill='blue', border='black')
        # Draw the back square
        drawPolygon(self.backPoints, fill='green', border='black')

        # Connect the front and back squares to simulate depth
        for i in range(4):
            drawLine(self.frontPoints[i][0], self.frontPoints[i][1], self.backPoints[i][0], self.backPoints[i][1])

    def move(self, dx, dy):
        # Move the cube in 2D space
        self.x += dx
        self.y += dy
        # Adjust points for the cube movement
        for i in range(4):
            self.frontPoints[i] = (self.frontPoints[i][0] + dx, self.frontPoints[i][1] + dy)
            self.backPoints[i] = (self.backPoints[i][0] + dx, self.backPoints[i][1] + dy)

class Game:
    def __init__(self, app):
        self.app = app
        self.reset()
    
    def reset(self):
        self.started = False
        self.cube = Cube(150, 150)
        self.dx = 5
        self.dy = 5

    def start(self):
        self.reset()
        self.started = True

    def update(self):
        if self.started:
            self.cube.move(self.dx, self.dy)

    def draw(self):
        if self.started:
            self.cube.draw()

def onAppStart(app):
    app.game = Game(app)

def onStep(app):
    app.game.update()

def onKeyPress(app, key):
    if key == 'p':
        app.game.start()

def redrawAll(app):
    app.game.draw()

def main():
    runApp()

main()
