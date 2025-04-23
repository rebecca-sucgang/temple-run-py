
# --- this is the magnet powerup ---
from cmu_graphics import *
import random
from PIL import Image as PILImage
import json 

# added leaderboard code by pranav
def loadScoresFromFile(): # AI helped with this function
    try:
        with open("my_scores.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"recentScore": 0, 
                "maxScore": 0,
                "pastScores": []}

class Player:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.r = radius

    def move(self, direction):
        if direction == 'left' and self.x - self.r > 150:
            self.x -=5
        elif direction == 'right' and self.x + self.r < 350:
            self.x += 5

    def draw(self):
        drawCircle(self.x, self.y, self.r, fill='lightblue')

    def getBounds(self):
        return (self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)

class Coin:
    def __init__(self, x, y): 
        self.x = x
        self.y = y
        self.size = 20
        self.coinImages = CMUImage(PILImage.open('src/images/classiccoin.png').resize((self.size, self.size)))
        

    def move(self, speed):
        self.y += speed

    def draw(self):
        drawImage(self.coinImages, self.x, self.y)

    def getBounds(self):
        return (self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size)

class Hole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 35
        self.w = 60
        self.h = 30

    def move(self, speed):
        self.y += speed

    def draw(self):
        drawRect(self.x, self.y, self.w, self.h, fill='black')

    def getBounds(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)
    
class Magnet:
    def __init__(self, x, y): 
        self.x = x
        self.y = y
        self.size = 30
        self.magentImages = CMUImage(PILImage.open('src/images/gamemagnet2.png').resize((self.size, self.size)))
        
    def move(self, speed):
        self.y += speed

    def draw(self):
        drawImage(self.magentImages, self.x, self.y)

    def getBounds(self):
        return (self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size)

class Game:
    def __init__(self, app):
        self.app = app
        self.scoreList = []
        self.coins = []
        self.magnets = []

        # backgrounds added by rebecca
        self.startBackground = CMUImage(PILImage.open('src/images/startcavelogo.png').resize((500, 500)))
        self.tutorialBackground = CMUImage(PILImage.open('src/images/tutorial.png').resize((500, 500)))
        self.forestBackground = CMUImage(PILImage.open('src/images/forestbackground.jpg').resize((500, 500)))
        self.gameOverBackground = CMUImage(PILImage.open('src/images/gameover.png').resize((500, 500)))
        # buttons by rebecca
        self.startButton = CMUImage(PILImage.open('src/images/buttons/start.png'))
        self.howToPlayButton = CMUImage(PILImage.open('src/images/buttons/howtoplay.png'))
        self.backButton = CMUImage(PILImage.open('src/images/buttons/back.png'))
        self.normalModeButton = CMUImage(PILImage.open('src/images/buttons/normalmode.png'))
        self.mazeModeButton = CMUImage(PILImage.open('src/images/buttons/mazemode.png'))
        self.leaderboardButton = CMUImage(PILImage.open('src/images/buttons/leaderboard.png'))
        self.startOverButton = CMUImage(PILImage.open('src/images/buttons/startover.png'))
        # code from pranav's leaderboard code
        scores = loadScoresFromFile()
        self.recentScore = scores["recentScore"]
        self.maxScore = scores["maxScore"]
        self.pastScores = scores.get("pastScores", [])
        #print("LOADED:", self.recentScore, self.maxScore)
        self.reset()

    def reset(self):
        self.started = False
        self.selectingMode = False
        self.tutorial = False
        self.leaderboard = False
        self.over = False
        self.paused = False
        self.score = 0
        self.speed = 5 # increased over time for diffuculty
        self.player = Player(200, 420, 15)
        self.hole = None  # Only one hole at a time
        self.coinTimer = 0
        self.roadOffset = 0 # vertical scroll for road
        self.roadSpeed = 2
        self.magnetTimer = 0 # note this is only for spawning the magnet
        self.magnetActive = False # ChatGPT suggested this line 
        self.magnetEffectTimer = 300 # note this marks the time the magnetic pulling coins effect lasts (AI helped)


    def start(self):
        self.reset()
        self.started = True

    def instructions(self):
        if not self.started:
            self.tutorial = True

    def leadership(self):
        if not self.started and not self.tutorial:
            self.leaderboard = True

    def togglePause(self):
        if self.started and not self.over:
            self.paused = not self.paused

    def distance(self, x1, y1, x2, y2): # pranav
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        return ((self.x2-self.x1)**2 + (self.y2-self.y1)**2)**0.5

    def update(self):

        if self.magnetActive == True: # ChatGPT provided guidance regarding this if statement
            self.magnetEffectTimer -= 1
            for coin in self.coins:
                dx = self.player.x - coin.x
                dy = self.player.y - coin.y
                dist = distance(self.player.x, coin.x, self.player.y, coin.y) # I wrote this distance function earlier 
                if dy <= 20:
                    attractionSpeed = 6
                    coin.x += dist*attractionSpeed
                    coin.y += dist*attractionSpeed
                    self.score += 1

            if self.magnetEffectTimer <= 0: # ChatGPT provided guidance for this if statement too!
                self.magnetActive = False
        


        if not self.started or self.over or self.paused:
            return
        
        # gradually increase speed over time
        self.speed = 5 + self.score // 15
        # Scroll the road
        self.roadOffset += self.roadSpeed
        if self.roadOffset >= 20:
            self.roadOffset -= 20

        # Generate coins in vertical columns on the road
        if self.coinTimer <= 0:
            x = random.randint(150, 350)  
            for i in range(5):
                self.coins.append(Coin(x, -i * 25))
            self.coinTimer = 40
        else:
            self.coinTimer -= 1

        if self.hole is None and random.random() < 0.03:
            self.hole = Hole(random.randint(170, 310), 0)

        for coin in self.coins:
            coin.move(self.speed)
        if self.hole:
            self.hole.move(self.speed)
        
        for magnet in self.magnets: # ChatGPT helped with this for loop 
            magnet.move(self.speed)
        

        playerBounds = self.player.getBounds()

        # Check if player got coins
        updatedCoins = []
        for coin in self.coins:
            if self.checkCollision(playerBounds, coin.getBounds()):
                self.incrementScore()
            else:
                updatedCoins.append(coin)

        # Remove coins that have gone off the screen 
        validCoins = []
        for coin in updatedCoins:
            if coin.y < 500: # 500 is screen width 
                validCoins.append(coin)  
        # Adds coin to validCoins list
        self.coins[:] = validCoins  

        # Generate a magnet on the road (pranav)
        if self.magnetTimer <= 0: 
            if(self.score >= 30) and (self.score % 30 == 0):
                x = random.randint(150, 350)
                y = random.randint(0, 400)
                self.magnets.append(Magnet(x, y))
                self.magnetTimer = 40
        else:
            self.magnetTimer -= 1


        # Check if player got a magnet (pranav)
        updatedMagnets = [] 
        for magnet in self.magnets:
            if self.checkCollision(playerBounds, magnet.getBounds()): # ChatGPT helped with this line
                self.incrementScore()
                self.magnetActive = True # ChatGPT helped with this line
                self.magnetEffectTimer = 300 # ChatGPT helped with this line
            else:
                updatedMagnets.append(magnet)

        # Remove magnets that have gone off the screen (pranav)
        validMagnets = []
        for magnet in updatedMagnets:
            if magnet.y < 500: # 500 is screen width
                validMagnets.append(magnet)
        # Adds magnet to validMagnets list
        self.magnets[:] = validMagnets


        # player falls in hole
        if self.hole:
            if self.checkCollision(playerBounds, self.hole.getBounds()):
                self.over = True
                self.scoreList.append(self.score)
                self.recentScore = self.score  # just to be sure
                self.end_game()  # 🔥 this saves the score to the file

            elif self.hole.y > 500:
                self.hole = None


        

    def incrementScore(self):
        self.score += 1
        return False

    def movePlayer(self, direction):
        if self.started and not self.over:
            self.player.move(direction)

    def checkCollision(self, a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)
    
    def returnMaxScore(self):  # pranav (guided by William Li - TA)
        if self.scoreList == []:
            return None
        else:
            return max(self.scoreList)
        
    def returnRecentScore(self): # pranav (guided by William Li - TA)
        if self.scoreList == []:
            return None
        else:
            return (self.scoreList)[-1]
        
    # added updated leaderboard by pranav
    def saveScoresToFile(self): # ChatGPT helped with this function

        if not hasattr(self, 'pastScores'): 
            self.pastScores = []

        self.pastScores.append(self.recentScore)
        self.pastScores = self.pastScores[-3:] # only keeping last 3 scores


        scores = {
            "recentScore": self.recentScore,
            "maxScore": self.maxScore,
            "pastScores" : self.pastScores
        }
        
        with open("my_scores.json", "w") as f:
            json.dump(scores, f, indent=4)

   
        
    def end_game(self): # ChatGPT also helped with this function 
        self.recentScore = self.score

        if self.score > self.maxScore:
            self.maxScore = self.score

        self.saveScoresToFile()

    def leaderShipBoard(self): # ChatGPT provided some guidance here
        drawLabel("Leaderboard", 250, 100, size=30, bold=True)
        drawLabel(f"Most Recent Score: {self.recentScore}", 250, 150)
        drawLabel(f"Maximum Score:     {self.maxScore}", 250, 190)
        drawLabel('Scores from the 3 most recent runs', 250, 230, size=18, bold=True)    
        for i in range(len(self.pastScores)): # ChatGPT helped with this for loop 
            runNumber = i
            runScore = self.pastScores[runNumber]
            drawLabel(f'Run {runNumber+1} : {runScore}', 250, 250+30*i)

    # end of pranav's leaderboard code
            
    def drawRoadBackground(self):
        drawImage(self.forestBackground, 0, 0)
        # Used ChatGPT to generate road background - after Hack112, I will do it myself
        for y in range(-40, 500, 20):
            offset = 10 if (y // 20) % 2 == 0 else 0
            for x in range(150 + offset, 350, 20):
                drawRect(x, y + self.roadOffset, 20, 20, fill='sienna', border='black', borderWidth=1)

    def draw(self):
        if self.tutorial:
            drawImage(self.tutorialBackground, 0, 0)
            drawImage(self.backButton, 200, 375)
        
        elif self.selectingMode:
            drawImage(self.startBackground, 0,0)
            drawImage(self.normalModeButton, 200, 310)
            drawImage(self.mazeModeButton, 200, 390)

        elif self.leaderboard: # pranav
       
            # added pranav's code here
            self.leaderShipBoard()
            drawImage(self.backButton, 200, 410)

        elif not self.started:
            drawImage(self.startBackground, 0,0)
            drawImage(self.startButton, 210, 290)
            drawImage(self.howToPlayButton, 210, 350)
            drawImage(self.leaderboardButton, 210, 410)

        elif self.paused:
            drawLabel('Paused', 200, 200, size=20, fill='orange', bold=True)
        
        elif self.over:
            drawImage(self.gameOverBackground, 0,0)

            drawLabel(f'{self.score}', 250, 260, size=60, fill='white', bold=True)
            drawImage(self.startOverButton, 200, 350)

    
        else:
            self.drawRoadBackground()
            self.player.draw()
            for coin in self.coins:
                coin.draw()
            if self.hole:
                self.hole.draw()
            for magnet in self.magnets: # ChatGPT helped with this for loop
                magnet.draw()
            if self.magnetActive:
                drawLabel(f'Magnet Effect Timer: {self.magnetEffectTimer//30} s', 70, 50, bold=True, fill = 'white')
            drawLabel(f'Score: {self.score}', 250, 20, size=18, bold=True, fill="white")

def onAppStart(app):
    app.game = Game(app)

def onStep(app):
    app.game.update()

def onKeyHold(app, keys):
    if 'left' in keys:
        app.game.movePlayer('left')
    if 'right' in keys:
        app.game.movePlayer('right')

# def onKeyPress(app, key):
#     if key == 'p':
#         app.game.togglePause()

def onMousePress(app, x, y):
    if app.game.tutorial:
        if 200 <= x <= 300 and 375 <= y <= 415:
            # Return to main menu
            app.game.tutorial = False

    elif app.game.leaderboard: 
        if 200 <= x <= 300 and 390 <= y <= 430:
            # Return to main menu
            app.game.leaderboard = False
    
    elif app.game.over:
        if 200 <= x <= 300 and 350 <= y <= 390:
            # Return to main menu
            app.game.reset()
    
    elif app.game.selectingMode:
        if 200 <= x <= 330 and 310 <= y <= 360:
            app.game.selectingMode = False
            app.game.start()  # start actual game

    elif not app.game.started:
        if 210 <= x <= 310 and 290 <= y <= 330:
            app.game.selectingMode = True

        elif 210 <= x <= 310 and 350 <= y <= 390:
            app.game.instructions()

        elif 210 <= x <= 310 and 410 <= y <= 450:
            app.game.leadership()

def redrawAll(app):
    app.game.draw()

def main():
    runApp(width=500, height=500)

main()

# class Magnet:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#         self.r = 12

#     # keep track of how long the magnet is active
#     def move(self, speed):
#         self.y += speed
    
#     def draw(self):
#         drawCircle(self.x, self.y, self.r, fill='red')
    
#     def getBounds(self):
#         return (self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)
    
# class Game:
#     def __init__(self, app):
#         pass

#     def reset(self):
#         self.magnets = []
#         self.magnetTimer = 200
#         self.magnetActive = False
#         self.magnetDuration = 0

#     def update(self):
#         if self.magnetTimer <= 0:
#             x = random.randint(100, 300) 
#             self.magnets.append(Magnet(x, 0))
#             self.magnetTimer = 400
#         else:
#             self.magnetTimer -= 1
        
#         # move the magnets down
#         for magnet in self.magnets:
#             magnet.move(self.speed)

#         # if magnet has been collected
#         updatedMagnets = []
#         for magnet in self.magnets:
#             if self.checkCollision(self.player.getBounds()):
#                 self.magnetActive = True
#                 self.magnetDuration = 300
#             elif magnet.y < 400:
#                 updatedMagnets.append(magnet)

#         self.magnets = updatedMagnets
        
#         # decrease magnet power-up time
#         if self.magnetActive:
#             self.magnetDuration -= 1
             
#             updatedCoins = []
#             for coin in self.coins:
#                 dx = self.player.x - coin.x

#             if self.magnetDuration <= 0:
#                 self.magnetActive = False


# NEXT FEW LINES OF CODE IS FOR THE RESURRECTION WINGS:


# class Wing: # this is a proxy for the resurrection wings 
#     def __init__(self, x, y): 
#         self.x = x
#         self.y = y
#         self.size = 10
        

#     def move(self, speed):
#         self.y += speed

#     def draw(self): # the star represents the resurection wings
#         drawStar(self.x, self.y, self.size, fill = 'pink', border = 'black')

#     def getBounds(self):
#         return (self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size)

    
# class Game:
#     def __init__(self, app):
#         pass

#     def reset(self):
#         self.wings = []
#         self.wingTimer = 200
#         self.wingActive = False
#         self.wingDuration = 0

#     def update(self):
#         if self.wingTimer <= 0:
#             x = random.randint(100, 300) 
#             self.wings.append(Wing(x, 0))
#             self.wingTimer = 400
#         else:
#             self.wingTimer -= 1
        
#         # move the wings down
#         for wing in self.wings:
#             wing.move(self.speed)

#         # if wing has been collected
#         updatedWings = []
#         for wing in self.wings:
#             if self.checkCollision(self.player.getBounds()):
#                 self.wingActive = True
#                 self.wingDuration = 300
#             elif wingt.y < 400:
#                 updatedWings.append(magnet)

#         self.wings = updatedWings
        
#         # decrease magnet power-up time
#         if self.wingActive:
#             self.wingDuration -= 1
             
#             updatedCoins = []
#             for coin in self.coins:
#                 dx = self.player.x - coin.x

#             if self.wingDuration <= 0:
#                 self.wingActive = False



# look back at notes and see what to modify in the code based on what I want
