from cmu_graphics import *

def onAppStart(app):
    app.roadSegments = []
    app.horizonY = 100
    app.bottomY = 400
    app.numSegments = 20
    app.speed = 3

    # Create segments
    for i in range(app.numSegments):
        app.roadSegments.append(createSegment(i, app))

def createSegment(index, app):
    '''Returns a segment as a dictionary with position info'''
    # How far the segment is from the horizon (0 is far away)
    t = index / app.numSegments
    y = interpolate(app.horizonY, app.bottomY, t)
    width = interpolate(50, 400, t)  # Narrow at top, wide at bottom
    return { 'y': y, 'width': width }

def interpolate(start, end, t):
    return start + (end - start) * t

def onStep(app):
    # Move all road segments downward
    for seg in app.roadSegments:
        seg['y'] += app.speed

    # Remove bottom segments that are off screen
    app.roadSegments = [seg for seg in app.roadSegments if seg['y'] < app.height]

    # Add new segment at the top
    while len(app.roadSegments) < app.numSegments:
        topSeg = app.roadSegments[0]
        newY = topSeg['y'] - app.speed
        newWidth = interpolate(50, 400, (newY - app.horizonY) / (app.bottomY - app.horizonY))
        app.roadSegments.insert(0, { 'y': newY, 'width': newWidth })

def redrawAll(app):
    # Sky
    drawRect(0, 0, app.width, app.height, fill='skyBlue')

    # Draw road segments as trapezoids
    for i in range(len(app.roadSegments)-1):
        seg1 = app.roadSegments[i]
        seg2 = app.roadSegments[i+1]

        # Left and right edges
        x1Left = app.width / 2 - seg1['width'] / 2
        x1Right = app.width / 2 + seg1['width'] / 2
        x2Left = app.width / 2 - seg2['width'] / 2
        x2Right = app.width / 2 + seg2['width'] / 2

        # Trapezoid (quad) from seg1 to seg2
        drawPolygon(x1Left, seg1['y'],
                    x1Right, seg1['y'],
                    x2Right, seg2['y'],
                    x2Left, seg2['y'],
                    fill='gray')

def main():
    runApp(width=400, height=400)

main()