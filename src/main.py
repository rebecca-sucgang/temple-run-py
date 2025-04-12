from cmu_graphics import *

def onAppStart(app):
    app.topRadius = 10
    app.bottomRadius = 10
    app.topCounter = 0
    app.bottomCounter = 0
    app.topPaused = True
    app.bottomPaused = True
    app.onStepCounter = 30
    

def redrawAll(app):
    drawLabel("Different Speeds", 200, 30, size = 16)
    drawLabel("Press t to pause/unpause top dot", 200, 50)
    drawLabel("Press b to pause/unpause bottom dot", 200, 70)
    
    drawCircle(200, 175, app.topRadius,
    fill = "gray" if app.topPaused else "cyan", border = "black")
    drawLabel(str(app.topCounter), 200, 175, size = 16)
    
    drawCircle(200, 325, app.bottomRadius,
    fill = "gray" if app.bottomPaused else "pink", border = "black")
    drawLabel(str(app.bottomCounter), 200, 325, size = 16)

def onStep(app):
    app.onStepCounter += 1
    if not app.topPaused:
        app.topCounter += 1
        if app.topRadius == 75:
            app.topRadius = 10
        else:
            app.topRadius += 5
    if not app.bottomPaused and app.onStepCounter % 5 == 0:
        app.bottomCounter += 1
        if app.bottomRadius == 75:
            app.bottomRadius = 10
        else:
            app.bottomRadius += 5

def onKeyPress(app, key):
    if key == "t":
        app.topPaused = not app.topPaused
    if key == "b":
        app.bottomPaused = not app.bottomPaused

def main():
    runApp()

main()