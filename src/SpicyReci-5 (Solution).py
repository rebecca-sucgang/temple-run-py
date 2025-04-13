import numpy as np
from lib import Vec3, Mat4
from types import SimpleNamespace
from cmu_graphics import *

################################################################################
# Triangle Functions

# For this code, we manage triangles using SimpleNamespaces

# This is because we need to sort triangles, so storing their information
# together makes things a lot easier
################################################################################

def makeTriangle(v1, v2, v3, color):
    triangle = SimpleNamespace()
    triangle.vertices = [v1, v2, v3]
    triangle.color = color
    return triangle

# Used for sorting triangles
# Note: This is just an approximation
def triangleDepth(triangle):
    return triangle.vertices[0].z + triangle.vertices[2].z

def drawTriangle(triangle):
    pointsList = []
    for vertex in triangle.vertices:
        pointsList.append(float(vertex.x))
        pointsList.append(float(vertex.y))
    drawPolygon(*pointsList, fill=triangle.color, border='black')

################################################################################
# Simple Shape Functions

# Note: These are fixed, but the coordinates are in local space, so we can 
#       still change properties about them by multiplying by different
#       transformation matrices 
################################################################################

def makeSquare(app):
    app.triangles = [None] * 2
    app.triangles[0] = makeTriangle(Vec3(-0.5, -0.5, 0), Vec3(0.5, 0.5, 0),
                             Vec3(-0.5, 0.5, 0), 'green')
    app.triangles[1] = makeTriangle(Vec3(-0.5, -0.5, 0), Vec3(0.5, -0.5, 0),
                             Vec3(0.5, 0.5, 0), 'green')
def makeCube(app):
    app.triangles = [None] * 12
    app.triangles[0] = makeTriangle(Vec3(-0.5, -0.5, -0.5), Vec3(0.5, -0.5, -0.5),
                             Vec3(0.5, 0.5, -0.5), 'green')
    app.triangles[1] = makeTriangle(Vec3(0.5, 0.5, -0.5), Vec3(-0.5, 0.5, -0.5),
                             Vec3(-0.5, -0.5, -0.5), 'green')
    app.triangles[2] = makeTriangle(Vec3(-0.5, -0.5, 0.5), Vec3(0.5, -0.5, 0.5),
                             Vec3(0.5, 0.5, 0.5), 'green')
    app.triangles[3] = makeTriangle(Vec3(0.5, 0.5, 0.5), Vec3(-0.5, 0.5, 0.5),
                             Vec3(-0.5, -0.5, 0.5), 'green')
    app.triangles[4] = makeTriangle(Vec3(-0.5, 0.5, 0.5), Vec3(-0.5, 0.5, -0.5),
                             Vec3(-0.5, -0.5, -0.5), 'green') 
    app.triangles[5] = makeTriangle(Vec3(-0.5, -0.5, -0.5), Vec3(-0.5, -0.5, 0.5),
                             Vec3(-0.5, 0.5, 0.5), 'green') 
    app.triangles[6] = makeTriangle(Vec3(0.5, 0.5, 0.5), Vec3(0.5, 0.5, -0.5),
                             Vec3(0.5, -0.5, -0.5), 'green') 
    app.triangles[7] = makeTriangle(Vec3(0.5, -0.5, -0.5), Vec3(0.5, -0.5, 0.5),
                             Vec3(0.5, 0.5, 0.5), 'green') 
    app.triangles[8] = makeTriangle(Vec3(-0.5, -0.5, -0.5), Vec3(0.5, -0.5, -0.5),
                             Vec3(0.5, -0.5, 0.5), 'green') 
    app.triangles[9] = makeTriangle(Vec3(0.5, -0.5, 0.5), Vec3(-0.5, -0.5, 0.5),
                             Vec3(-0.5, -0.5, -0.5), 'green')   
    app.triangles[10] = makeTriangle(Vec3(-0.5, 0.5, -0.5), Vec3(0.5, 0.5, -0.5),
                             Vec3(0.5, 0.5, 0.5), 'green') 
    app.triangles[11] = makeTriangle(Vec3(0.5, 0.5, 0.5), Vec3(-0.5, 0.5, 0.5),
                             Vec3(-0.5, 0.5, -0.5), 'green') 

################################################################################
# Sample Square Code
################################################################################     

def onAppStart(app):
    makeSquare(app)
    app.steps = 0

def redrawAll(app):
    transform = Mat4.scale(Vec3(0.5, 0.75, 0))
    transform = Mat4.rotate(np.radians(app.steps), Vec3(0.0, 0.0, 1.0)) @ transform
    transform = Mat4.screenSpace(app.width, app.height) @ transform
    transform = Mat4.translate(Vec3(50, 100, 0)) @ transform
    
    newTriangles = []
    for triangle in app.triangles:
        vertexList = []
        for vertex in triangle.vertices:
            newPos = transform @ vertex
            vertexList.append(newPos)
        newTriangles.append(makeTriangle(*vertexList, triangle.color))

    for triangle in newTriangles:
        drawTriangle(triangle)

def onStep(app):
    app.steps = (app.steps + 1) % 360              

################################################################################
# Sample Cube Code
################################################################################     

def onAppStart(app):
    makeCube(app)
    app.steps = 0
    app.cubePosition = 0
    app.dz = 0.1

def redrawAll(app):
    model = Mat4.rotate(np.radians(app.steps), Vec3(0.5, 1.0, 0.0))
    model = Mat4.translate(Vec3(0, 0, app.cubePosition)) @ model
    view = Mat4.lookAt(Vec3(0, 0, 3), Vec3(0, 0, 0), Vec3(0, 1, 0))
    projection = Mat4.perspective(np.radians(45.0), app.width / app.height, 0.1, 100)
    screenSpace = Mat4.screenSpace(app.width, app.height)
    transform = screenSpace @ projection @ view @ model
    
    newTriangles = []
    for triangle in app.triangles:
        vertexList = []
        for vertex in triangle.vertices:
            newPos = transform @ vertex
            vertexList.append(newPos)
        newTriangles.append(makeTriangle(*vertexList, triangle.color))

    newTriangles.sort(reverse=True, key=triangleDepth)
    for triangle in newTriangles:
        drawTriangle(triangle)

def onStep(app):
    app.steps = (app.steps + 1) % 360
    app.cubePosition += app.dz
    if app.cubePosition > 0.5:
        app.cubePosition = 0.5
        app.dz = -0.1
    elif app.cubePosition < -5:
        app.cubePosition = -5
        app.dz = 0.1

################################################################################

def main():
    runApp()

if __name__ == '__main__':
    main()