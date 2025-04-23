from cmu_graphics import *
import random
from PIL import Image as PILImage
from ui_assets import UIBackground, UIButton
import json

# added leaderboard code by pranav
def loadScoresFromFile():
    try:
        with open("my_scores.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"recentScore": 0, 
                "maxScore": 0,
                "pastScores": []}

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        # i asked chatgpt for help 
        # on how to create my own sprite and integrating into code

        # Runner sprite, with help of ChatGPT
        self.runnerFrameWidth = 186 # actual size
        self.runnerFrameHeight = 396 # actual size
        self.runnerDisplayWidth = 50 # size on screen
        self.runnerDisplayHeight = 100 #  size on screen
        self.frameIndex = 0
        self.frameCount = 6
        self.frameSize = 200
        self.tick = 0

        # Jump sprite, with help of ChatGPT
        self.jumpFrameWidth = 400 # actual size
        self.jumpFrameHeight = 400 # actual size
        self.jumpDisplayWidth = 100 # size on screen
        self.jumpDisplayHeight = 100 # size on screen
        
        # Jump sprite, with help of ChatGPT
        self.isJumping = False
        self.jumpFrameIndex = 0
        self.jumpFrameCount = 8
        self.jumpHeight = 50
        self.jumpProgress = 0
        self.jumpUpDuration = 8
        self.jumpDownDuration = 8
        self.jumpTotalFrames = self.jumpUpDuration + self.jumpDownDuration

    def startJump(self): # with help of ChatGPT
        if not self.isJumping:
            self.isJumping = True
            self.jumpFrameIndex = 0
            self.jumpProgress = 0
    
    def updateJump(self): # with help of ChatGPT
        if self.isJumping:
            self.jumpFrameIndex = (self.jumpFrameIndex + 1) % self.jumpFrameCount
            self.jumpProgress += 1

            if self.jumpProgress <= self.jumpUpDuration:
                self.y -= self.jumpHeight / self.jumpUpDuration
            elif self.jumpProgress <= self.jumpTotalFrames:
                self.y += self.jumpHeight / self.jumpDownDuration
            else:
                self.isJumping = False
                self.jumpProgress = 0

    def move(self, direction, speed):
        if self.isJumping:
            halfWidth = self.jumpDisplayWidth // 2
        else:
            halfWidth = self.runnerDisplayWidth // 2        
        
        if direction == 'left' and self.x - halfWidth > 150:
            self.x -= speed
        elif direction == 'right' and self.x + halfWidth < 350:
            self.x += speed

    def updateAnimation(self): # animation only updates if the game isnt paused
        self.tick += 1
        if self.tick % 5 == 0:
            self.frameIndex = (self.frameIndex + 1) % self.frameCount

    def draw(self): # guidance from ChatGPT
        if self.isJumping: # jumping sprite
            spriteSheet = PILImage.open('src/images/sprites/jumpspritesheet.png')
            frameWidth = self.jumpFrameWidth
            frameHeight = self.jumpFrameHeight
            displayWidth = self.jumpDisplayWidth
            displayHeight = self.jumpDisplayHeight
            frameIndex = self.jumpFrameIndex
            left = frameIndex * frameWidth
        else: # runner sprite
            if self.tick % 5 == 0:
                self.frameIndex = (self.frameIndex + 1) % self.frameCount
            spriteSheet = PILImage.open('src/images/sprites/runnerspritesheet.png')
            frameWidth = self.runnerFrameWidth
            frameHeight = self.runnerFrameHeight
            displayWidth = self.runnerDisplayWidth
            displayHeight = self.runnerDisplayHeight
            frameIndex = self.frameIndex
            left = frameIndex * frameWidth

        cropped = spriteSheet.crop((left, 0, left + frameWidth, frameHeight))
        resized = cropped.resize((displayWidth, displayHeight))
        drawImage(CMUImage(resized), self.x - displayWidth // 2, self.y - displayHeight // 2)

    def getBounds(self):
        if self.isJumping: # check if jumping sprite
            displayWidth = self.jumpDisplayWidth
            displayHeight = self.jumpDisplayHeight
        else: # check if running sprite
            displayWidth = self.runnerDisplayWidth
            displayHeight = self.runnerDisplayHeight
        return (self.x - displayWidth // 2,
                self.y - displayHeight // 2,
                self.x + displayWidth // 2,
                self.y + displayHeight // 2)

class Coin:
    def __init__(self, x, y): 
        self.x = x
        self.y = y
        self.size = 20
        self.coinImages = CMUImage(
            PILImage.open('src/images/classiccoin.png').resize(
                (self.size, self.size)))

    def move(self, speed):
        self.y += speed

    def draw(self):
        drawImage(self.coinImages, self.x, self.y)

    def getBounds(self):
        return (self.x - self.size, self.y - self.size, 
                self.x + self.size, self.y + self.size)

class Hole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 60
        self.h = 30

    def move(self, speed):
        self.y += speed

    def draw(self):
        drawRect(self.x, self.y, self.w, self.h, fill='black')

    def getBounds(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)

class Game:
    def __init__(self, app):
        self.app = app
        self.scoreList = []
        self.coins = []
        self.UIBackground = UIBackground()
        self.UIButton = UIButton()
        
        self.music = Sound('sounds/templerunmusic.mp3')
        self.musicPaused = False
        self.music.play(loop=True)

        # code from pranav's leaderboard code
        scores = loadScoresFromFile()
        self.recentScore = scores["recentScore"]
        self.maxScore = scores["maxScore"]
        self.pastScores = scores.get("pastScores", [])

        self.reset()

    def reset(self):
        self.started = False
        self.selectingMode = False
        self.tutorial = False
        self.mazeTutorial = False
        self.leaderboard = False
        self.over = False
        self.paused = False
        self.score = 0
        self.speed = 5 # increased over time for diffuculty
        self.player = Player(250, 440)
        self.hole = None  # Only one hole at a time
        self.coinTimer = 0
        self.roadOffset = 0 # vertical scroll for road
        self.roadSpeed = 2

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

    def toggleMusic(self):
        if self.musicPaused:
            self.music.play(loop=True)
        else:
            self.music.pause()
        self.musicPaused = not self.musicPaused

    def update(self):
        if not self.started or self.over or self.paused:
            return
        
        self.player.updateAnimation()
        self.player.updateJump()
        
        # gradually increase speed over time
        self.speed = 5 + self.score // 10
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

        playerBounds = self.player.getBounds()

        # Check if player got coins
        updatedCoins = []
        for coin in self.coins:
            if self.checkCollision(playerBounds, coin.getBounds()):
                self.incrementScore(coin)
            else:
                updatedCoins.append(coin)

        # Remove coins that have gone off the screen 
        validCoins = []
        for coin in updatedCoins:
            if coin.y < 500: # 500 is screen width 
                validCoins.append(coin)  
        # Adds coin to validCoins list
        self.coins = validCoins

        # player falls in hole
        if self.hole:
            if self.checkCollision(playerBounds, self.hole.getBounds()):
                self.over = True
                self.scoreList.append(self.score)
                self.recentScore = self.score  # just to be sure
                self.endGame()  # this saves the score to the file

            elif self.hole.y > 500:
                self.hole = None

    def incrementScore(self, coin):
        self.score += 1
        return False

    def movePlayer(self, direction):
        if self.started and not self.over:
            self.player.move(direction, self.speed)

    def checkCollision(self, a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)
    
    def returnMaxScore(self):  # pranav added this function
        if self.scoreList == []:
            return None
        else:
            return max(self.scoreList)
        
    def returnRecentScore(self): # pranav added this function
        if self.scoreList == []:
            return None
        else:
            return (self.scoreList)[-1]
        
    # added updated leaderboard by pranav
    def saveScoresToFile(self):
        if not hasattr(self, 'pastScores'):
            self.pastScores = []

        self.pastScores.append(self.recentScore)
        self.pastScores = self.pastScores[-3:] # maintaining last 3 scores only

        scores = {
            "recentScore": self.recentScore,
            "maxScore": self.maxScore,
            "pastScores": self.pastScores
        }

        with open("my_scores.json", "w") as f:
            json.dump(scores, f, indent=4)
        
    def endGame(self):
        self.recentScore = self.score

        if self.score > self.maxScore:
            self.maxScore = self.score

        self.saveScoresToFile()

    def leaderShipBoard(self):
        drawImage(self.UIBackground.leaderboardBackground, 0, 0)
        drawLabel(f"{self.recentScore}", 350, 123, 
                  fill='white', size=18, bold=True)
        drawLabel(f"{self.maxScore}", 330, 161, 
                  fill='white', size=18, bold=True)
        for i in range(len(self.pastScores)):
            runNumber = i
            runScore = self.pastScores[runNumber]
            drawLabel(f'{runScore}', 300, 297+37*i, 
                      fill='white', size=18, bold=True)

    # end of pranav's leaderboard code
            
    def drawRoadBackground(self):
        drawImage(self.UIBackground.forestBackground, 0, 0)
        # Used ChatGPT to generate road background
        for y in range(-40, 500, 20):
            offset = 10 if (y // 20) % 2 == 0 else 0
            for x in range(150 + offset, 350, 20):
                drawRect(x, y + self.roadOffset, 20, 20, 
                         fill='sienna', border='black', borderWidth=1)
                
        # if step reaches a certain amount, draw
                
    def drawSoundIcon(self):
        drawImage(self.UIButton.soundButton, 20, 430)
        if self.musicPaused:
            drawLine(20, 430, 70, 480, fill='red', lineWidth=4)

    # organized draw helper functions
    def drawTutorial(self):
        drawImage(self.UIBackground.tutorialNormal, 0, 0)
        drawImage(self.UIButton.backButton, 110, 410)
        self.drawSoundIcon()

    def drawMazeTutorial(self):
        drawImage(self.UIBackground.tutorialMaze, 0, 0)
        drawImage(self.UIButton.backButton, 110, 410)
        self.drawSoundIcon()

    def drawSelectingMode(self):
        drawImage(self.UIBackground.startBackground, 0,0)
        drawImage(self.UIButton.normalModeButton, 200, 285)
        drawImage(self.UIButton.mazeModeButton, 200, 350)
        drawImage(self.UIButton.backButton, 215, 415)
        self.drawSoundIcon()

    def drawLeaderboard(self):
        # added pranav's code here
        self.leaderShipBoard()
        drawImage(self.UIButton.backButton, 200, 410)
        self.drawSoundIcon()
    
    def drawNotStarted(self):
        drawImage(self.UIBackground.startBackground, 0,0)
        drawImage(self.UIButton.startButton, 210, 290)
        drawImage(self.UIButton.howToPlayButton, 210, 350)
        drawImage(self.UIButton.leaderboardButton, 210, 410)
        self.drawSoundIcon()

    def drawOver(self):
        drawImage(self.UIBackground.gameOverBackground, 0,0)
        drawLabel(f'{self.score}', 250, 260, 
                    size=60, fill='white', bold=True)
        drawImage(self.UIButton.startOverButton, 200, 350)
        self.drawSoundIcon()

    def drawPaused(self):
        self.drawRoadBackground()
        self.player.draw()
        for coin in self.coins:
            coin.draw()
        if self.hole:
            self.hole.draw()
        drawLabel(f'Score: {self.score}', 250, 20, 
                    size=18, bold=True, fill="white")
        drawLabel('Paused', 250, 60, 
                    size=24, fill='orange', bold=True)
        drawImage(self.UIButton.playButton, 410, 420)
        self.drawSoundIcon()

    def drawActualGame(self):
        self.drawRoadBackground()
        self.player.draw()
        for coin in self.coins:
            coin.draw()
        if self.hole:
            self.hole.draw()
        drawLabel(f'Score: {self.score}', 250, 20, 
                    size=18, bold=True, fill="white")
        drawImage(self.UIButton.pauseButton, 423, 433)
        self.drawSoundIcon()

    def draw(self):
        if self.tutorial:
            self.drawTutorial()
        
        elif self.mazeTutorial:
            self.drawMazeTutorial()
        
        elif self.selectingMode:
            self.drawSelectingMode()

        elif self.leaderboard:
            self.drawLeaderboard()

        elif not self.started:
            self.drawNotStarted()
        
        elif self.over:
            self.drawOver()

        elif self.paused:
            self.drawPaused()

        else:
            self.drawActualGame()

def onAppStart(app):
    app.game = Game(app)

def onStep(app):
    app.game.update()

def onKeyPress(app, key):
    if app.game.started and not app.game.over and not app.game.paused:
        if key == 'up':
            app.game.player.startJump()

def onKeyHold(app, keys):
    # cannot move player when paused
    if app.game.started and not app.game.over and not app.game.paused:
        if 'left' in keys:
            app.game.movePlayer('left')
        if 'right' in keys:
            app.game.movePlayer('right')

def onMousePress(app, x, y):
    if app.game.started and not app.game.over:
        if 20 <= x <= 80 and 420 <= y <= 480:
            app.game.toggleMusic()
        if 410 <= x <= 470 and 420 <= y <= 470:
            app.game.togglePause()
            return

    elif app.game.tutorial:
        if 20 <= x <= 80 and 420 <= y <= 480:
            app.game.toggleMusic()
        if 110 <= x <= 210 and 410 <= y <= 450:
            # Return to main menu
            app.game.tutorial = False
        if __ <= x <= __ and 410 <= y <= 460:
            pass

    elif app.game.leaderboard: 
        if 20 <= x <= 80 and 420 <= y <= 480:
            app.game.toggleMusic()
        if 200 <= x <= 300 and 390 <= y <= 430:
            app.game.leaderboard = False
    
    elif app.game.over:
        if 200 <= x <= 300 and 350 <= y <= 390:
            app.game.reset()
        if 20 <= x <= 80 and 420 <= y <= 480:
            app.game.toggleMusic()
    
    elif app.game.selectingMode:
        if 200 <= x <= 330 and 285 <= y <= 335:
            app.game.selectingMode = False
            app.game.start()  # start actual game
        if 20 <= x <= 80 and 420 <= y <= 480:
            app.game.toggleMusic()
        if 210 <= x <= 310 and 415 <= y <= 465:
            app.game.reset()

    elif not app.game.started:
        if 210 <= x <= 310 and 290 <= y <= 330:
            app.game.selectingMode = True
        if 20 <= x <= 80 and 420 <= y <= 480:
            app.game.toggleMusic()
        elif 210 <= x <= 310 and 350 <= y <= 390:
            app.game.instructions()
        elif 210 <= x <= 310 and 410 <= y <= 450:
            app.game.leadership()

def redrawAll(app):
    app.game.draw()

def main():
    runApp(width=500, height=500)

main()