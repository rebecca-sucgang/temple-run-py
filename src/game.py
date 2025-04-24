from cmu_graphics import *
import random
from PIL import Image as PILImage
from ui_assets import UIBackground, UIButton
from mazecopy import MazeGame
import json

# added leaderboard code by pranav (with ChatGPT help)

# this function was written with help of ChatGPT
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
        self.jumpHeight = 80
        self.jumpProgress = 0
        self.jumpUpDuration = 12
        self.jumpDownDuration = 12
        self.jumpTotalFrames = self.jumpUpDuration + self.jumpDownDuration

    def startJump(self):  # with help of ChatGPT
        if not self.isJumping:
            self.isJumping = True
            self.jumpFrameIndex = 0
            self.jumpProgress = 0
    
    def updateJump(self):
        if self.isJumping:
            self.jumpFrameIndex = (self.jumpFrameIndex + 1)%self.jumpFrameCount
            self.jumpProgress += 1

            totalJumpFrames = self.jumpUpDuration + self.jumpDownDuration

            if self.jumpProgress <= self.jumpUpDuration:
                # Go up smoothly
                self.y -= self.jumpHeight / self.jumpUpDuration
            elif self.jumpProgress <= totalJumpFrames + 1:
                # Come down smoothly
                self.y += self.jumpHeight / self.jumpDownDuration
            else:
                # End jump
                self.isJumping = False
                self.jumpProgress = 0
            maxY = 400
            if self.y > maxY:
                self.y = maxY


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

    def draw(self): # the following code was guidance from ChatGPT
        if self.isJumping: # jumping sprite
            spriteSheet = PILImage.open('src/images/sprites/jumpspritesheet.png')
            # Video I used to screenshot and create the player sprite sheet:
            # https://www.youtube.com/watch?v=fuQf-iGCmKA
            frameWidth = self.jumpFrameWidth
            frameHeight = self.jumpFrameHeight
            displayWidth = self.jumpDisplayWidth
            displayHeight = self.jumpDisplayHeight
            frameIndex = self.jumpFrameIndex
            left = frameIndex * frameWidth
        else: # runner sprite
            spriteSheet = PILImage.open('src/images/sprites/runnerspritesheet.png')
            # Video I used to screenshot and create the player sprite sheet:
            # https://www.youtube.com/watch?v=fuQf-iGCmKA
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
        self.w = 100
        self.h = 30

    def move(self, speed):
        self.y += speed

    def draw(self):
        drawRect(self.x, self.y, self.w, self.h, fill='black')

    def getBounds(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)
    
class Magnet: # pranav
    def __init__(self, x, y): 
        self.x = x
        self.y = y
        self.size = 30
        self.magentImages = CMUImage(
            PILImage.open('src/images/gamemagnet2.png').resize(
                (self.size, self.size)))
        
    def move(self, speed):
        self.y += speed

    def draw(self):
        drawImage(self.magentImages, self.x, self.y)

    def getBounds(self):
        return (self.x - self.size, self.y - self.size, 
                self.x + self.size, self.y + self.size)

class Game:
    def __init__(self, app):
        self.app = app
        self.scoreList = []
        self.coins = []
        self.magnets = [] #ChatGPT helped with this
        self.UIBackground = UIBackground()
        self.UIButton = UIButton()
        
        self.music = Sound('sounds/templerunmusic.mp3')
        self.musicPaused = False
        self.music.play(loop=True)
        self.monkeySound = Sound('sounds/monkeysoundeffect.mp3')
        self.jumpSound = Sound('sounds/gruntjump.mp3')

        # code from pranav's leaderboard code (with help from ChatGPT)
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
        self.magnetTimer = 0 
        self.magnetActive = False 
        self.magnetEffectTimer = 300 

    def start(self):
        self.reset()
        self.started = True
        self.monkeySound.play()
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

    def distance(self, x1, y1, x2, y2): # pranav wrote this function 
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        return ((self.x2-self.x1)**2 + (self.y2-self.y1)**2)**0.5

    def toggleMusic(self):
        if self.musicPaused:
            self.music.play(loop=True)
        else:
            self.music.pause()
        self.musicPaused = not self.musicPaused

    def update(self):
        if self.magnetActive:
            self.handle_magnet_effect()

        if not self.started or self.over or self.paused:
            return

        self.update_player_state()
        self.update_road_offset()
        self.spawn_coins()
        self.spawn_hole()
        self.move_objects()
        self.handle_coin_collisions()
        self.cleanup_coins()
        self.spawn_magnets()
        self.handle_magnet_collisions()
        self.cleanup_magnets()
        self.check_hole_collision()

    def handle_magnet_effect(self):
        self.magnetEffectTimer -= 1
        for coin in self.coins:
            dx = self.player.x - coin.x
            dy = self.player.y - coin.y
            dist = distance(self.player.x, coin.x, self.player.y, coin.y)
            if dy <= 20:
                attractionSpeed = 6
                coin.x += dist * attractionSpeed
                coin.y += dist * attractionSpeed
                self.score += 1
        if self.magnetEffectTimer <= 0:
            self.magnetActive = False

    def update_player_state(self):
        self.player.updateAnimation()
        self.player.updateJump()
        self.speed = 5 + self.score // 15

    def update_road_offset(self):
        roadSpeed = self.roadSpeed * 0.5 if self.player.isJumping else self.roadSpeed
        self.roadOffset += roadSpeed
        if self.roadOffset >= 20:
            self.roadOffset -= 20

    def spawn_coins(self):
        if self.coinTimer <= 0:
            x = random.randint(150, 350)
            for i in range(5):
                self.coins.append(Coin(x, -i * 25))
            self.coinTimer = 40
        else:
            self.coinTimer -= 1

    def spawn_hole(self):
        if self.hole is None and random.random() < 0.03:
            holeWidth = 100
            minX = 150
            maxX = 350 - holeWidth
            holeX = random.randint(minX, maxX)
            self.hole = Hole(holeX, 0)

    def move_objects(self):
        for coin in self.coins:
            coin.move(self.speed)
        if self.hole:
            self.hole.move(self.speed)
        for magnet in self.magnets:
            magnet.move(self.speed)

    def handle_coin_collisions(self):
        playerBounds = self.player.getBounds()
        updatedCoins = []
        for coin in self.coins:
            if self.checkCollision(playerBounds, coin.getBounds()):
                self.incrementScore()
            else:
                updatedCoins.append(coin)
        self.coins = updatedCoins

    def cleanup_coins(self):
        self.coins = [coin for coin in self.coins if coin.y < 500]

    def spawn_magnets(self):
        if self.magnetTimer <= 0:
            if self.score >= 30 and self.score % 30 == 0:
                x = random.randint(150, 350)
                y = random.randint(0, 400)
                self.magnets.append(Magnet(x, y))
                self.magnetTimer = 40
        else:
            self.magnetTimer -= 1

    def handle_magnet_collisions(self):
        playerBounds = self.player.getBounds()
        updatedMagnets = []
        for magnet in self.magnets:
            if self.checkCollision(playerBounds, magnet.getBounds()):
                self.incrementScore()
                self.magnetActive = True
                self.magnetEffectTimer = 300
            else:
                updatedMagnets.append(magnet)
        self.magnets = updatedMagnets

    def cleanup_magnets(self):
        self.magnets = [magnet for magnet in self.magnets if magnet.y < 500]

    def check_hole_collision(self):
        if self.hole:
            playerBounds = self.player.getBounds()
            if self.checkCollision(playerBounds, self.hole.getBounds(), player=self.player, checkForHole=True):
                self.over = True
                self.scoreList.append(self.score)
                self.recentScore = self.score
                self.endGame()
            elif self.hole.y > 500:
                self.hole = None


    def incrementScore(self):
        self.score += 1
        return False

    def movePlayer(self, direction):
        if self.started and not self.over:
            self.player.move(direction, self.speed)

    def checkCollision(self, a, b, player=None, checkForHole=False):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b

        # If the collision check is for a hole, and the player is jumping
        if checkForHole and player.isJumping and player is not None:
            return False

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
        
    # added updated leaderboard by pranav (with the help of ChatGPT)
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
        
    def endGame(self): # pranav (this was written with help of ChatGPT)
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
        for i in range(len(self.pastScores)): #pranav (with ChatGPT guidance)
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
        drawImage(self.UIButton.leftArrowButton, 300, 410)
        drawImage(self.UIButton.rightArrowButton, 355, 410)
        self.drawSoundIcon()

    def drawMazeTutorial(self):
        drawImage(self.UIBackground.tutorialMaze, 0, 0)
        drawImage(self.UIButton.backButton, 110, 410)
        drawImage(self.UIButton.leftArrowButton, 300, 410)
        drawImage(self.UIButton.rightArrowButton, 355, 410)
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
        drawLabel(f'Score: {self.score}', 425, 20, 
                    size=18, bold=True, fill="white")
        drawImage(self.UIBackground.pausedLogo, 127, 200)
        drawImage(self.UIButton.playButton, 77, 420)
        drawImage(self.UIButton.backButton, 380, 433)
        self.drawSoundIcon()

    def drawActualGame(self):
        self.drawRoadBackground()
        for coin in self.coins:
            coin.draw()
        if self.hole:
            self.hole.draw()
        self.player.draw()
        for magnet in self.magnets: # ChatGPT helped with this for loop
                magnet.draw()
        if self.magnetActive: # ChatGPT guided with the drawLabel 
            drawLabel(f'Magnet Effect Timer: {self.magnetEffectTimer//30}', 
                      80, 20, size = 16, bold=True, fill = 'white')
        drawLabel(f'Score: {self.score}', 425, 20, 
                    size=18, bold=True, fill="white")
        drawImage(self.UIButton.pauseButton, 90, 433)
        drawImage(self.UIButton.backButton, 380, 433)
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
    app.gameMode = 'main' # asked ChatGPT how to link the mazemode
    app.mainGame = Game(app)
    app.mazeGame = MazeGame(app)

def onStep(app):
    if app.gameMode == 'main':
        app.mainGame.update()
    elif app.gameMode == 'maze':
        app.mazeGame.onStep(app) # handles all on step in maze mode

def onKeyPress(app, key):
    if app.gameMode == 'main':
        if (app.mainGame.started and not app.mainGame.over and not 
            app.mainGame.paused):
            if key == 'up' and not app.mainGame.player.isJumping:
                app.mainGame.player.startJump()
                app.mainGame.jumpSound.play()
    elif app.gameMode == 'maze': # handles all key presses in maze mode
        app.mazeGame.onKeyPress(app, key)

def onKeyHold(app, keys):
    if app.gameMode == 'main':
        # cannot move player when paused
        if (app.mainGame.started and not 
            app.mainGame.over and not app.mainGame.paused):
            if 'left' in keys:
                app.mainGame.movePlayer('left')
            if 'right' in keys:
                app.mainGame.movePlayer('right')
    if app.gameMode == 'maze': # handles all key holds in maze mode
        app.mazeGame.onKeyHold(app, keys)

def onKeyRelease(app, key):
    if app.gameMode == 'maze':
        app.mazeGame.onKeyRelease(app, key)

def onMousePress(app, x, y):
    if app.gameMode == 'main':
        handleMainModeMousePress(app, x, y)
    elif app.gameMode == 'maze':
        app.mazeGame.onMousePress(app, x, y)

def handleMainModeMousePress(app, x, y):
    if app.mainGame.started and not app.mainGame.over:
        handleGamePlayingMousePress(app, x, y)
    elif app.mainGame.tutorial:
        handleTutorialMousePress(app, x, y)
    elif app.mainGame.mazeTutorial:
        handleMazeTutorialMousePress(app, x, y)
    elif app.mainGame.leaderboard:
        handleLeaderboardMousePress(app, x, y)
    elif app.mainGame.over:
        handleGameOverMousePress(app, x, y)
    elif app.mainGame.selectingMode:
        handleModeSelectMousePress(app, x, y)
    elif not app.mainGame.started:
        handleMainMenuMousePress(app, x, y)


# Sub-handlers for different screens:

def handleGamePlayingMousePress(app, x, y):
    if 20 <= x <= 80 and 420 <= y <= 480:
        app.mainGame.toggleMusic()
    if 90 <= x <= 150 and 433 <= y <= 483:
        app.mainGame.togglePause()
    if 380 <= x <= 480 and 433 <= y <= 483:
        app.mainGame.reset()

def handleTutorialMousePress(app, x, y):
    if 20 <= x <= 80 and 420 <= y <= 480:
        app.mainGame.toggleMusic()
    if 110 <= x <= 210 and 410 <= y <= 450:
        app.mainGame.tutorial = False
    if 300 <= x <= 350 and 410 <= y <= 460:
        app.mainGame.tutorial = True
        app.mainGame.mazeTutorial = False
    if 355 <= x <= 405 and 410 <= y <= 460:
        app.mainGame.mazeTutorial = True
        app.mainGame.tutorial = False

def handleMazeTutorialMousePress(app, x, y):
    if 20 <= x <= 80 and 420 <= y <= 480:
        app.mainGame.toggleMusic()
    if 110 <= x <= 210 and 410 <= y <= 450:
        app.mainGame.mazeTutorial = False
    if 300 <= x <= 350 and 410 <= y <= 460:
        app.mainGame.tutorial = True
        app.mainGame.mazeTutorial = False
    if 355 <= x <= 405 and 410 <= y <= 460:
        app.mainGame.mazeTutorial = True
        app.mainGame.tutorial = False

def handleLeaderboardMousePress(app, x, y):
    if 20 <= x <= 80 and 420 <= y <= 480:
        app.mainGame.toggleMusic()
    if 200 <= x <= 300 and 390 <= y <= 430:
        app.mainGame.leaderboard = False

def handleGameOverMousePress(app, x, y):
    if 200 <= x <= 300 and 350 <= y <= 390:
        app.mainGame.reset()
    if 20 <= x <= 80 and 420 <= y <= 480:
        app.mainGame.toggleMusic()

def handleModeSelectMousePress(app, x, y):
    if 200 <= x <= 330 and 285 <= y <= 345:
        app.mainGame.selectingMode = False
        app.mainGame.start()
    if 200 <= x <= 330 and 350 <= y <= 390:
        app.gameMode = 'maze'
    if 20 <= x <= 80 and 420 <= y <= 480:
        app.mainGame.toggleMusic()
    if 210 <= x <= 310 and 415 <= y <= 465:
        app.mainGame.reset()

def handleMainMenuMousePress(app, x, y):
    if 210 <= x <= 310 and 290 <= y <= 330:
        app.mainGame.selectingMode = True
    if 20 <= x <= 80 and 420 <= y <= 480:
        app.mainGame.toggleMusic()
    elif 210 <= x <= 310 and 350 <= y <= 390:
        app.mainGame.instructions()
    elif 210 <= x <= 310 and 410 <= y <= 450:
        app.mainGame.leadership()


def redrawAll(app):
    if app.gameMode == 'main':
        app.mainGame.draw()
    elif app.gameMode == 'maze': # handles all drawing in maze mode
        app.mazeGame.redrawAll(app)

def main():
    runApp(width=500, height=500)

main()