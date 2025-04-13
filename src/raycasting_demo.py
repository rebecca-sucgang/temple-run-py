from cmu_graphics import *

def redrawAll(app):
    drawCircle(100, 100, 20, fill='purple')
    drawCircle(300, 300, 20, fill='orange')
    drawCircle(transformX(app, 100), 100, 20, fill='red')

def transformX(app, xOld):
    newX = (200 + xOld - 200)/(app.height + 200) * (xOld-200) + 200

def main():
    runApp()

main()