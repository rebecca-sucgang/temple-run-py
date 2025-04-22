from cmu_graphics import *
from PIL import Image as PILImage

class UIGame:
    def __init__(self):
        # Backgrounds
        self.startBackground = CMUImage(
            PILImage.open('src/images/startcavelogo.png').resize((500, 500)))
        self.tutorialBackground = CMUImage(
            PILImage.open('src/images/tutorial.png').resize((500, 500)))
        self.forestBackground = CMUImage(
            PILImage.open('src/images/forestbackground.jpg').resize((500, 500)))
        self.gameOverBackground = CMUImage(
            PILImage.open('src/images/gameover.png').resize((500, 500)))
        self.leaderboardBackground = CMUImage(
            PILImage.open('src/images/leaderboard.png').resize((500, 500)))

        # Buttons
        self.startButton = CMUImage(
            PILImage.open('src/images/buttons/start.png'))
        self.soundButton = CMUImage(
            PILImage.open('src/images/buttons/sound.png').resize((50, 50)))
        self.howToPlayButton = CMUImage(
            PILImage.open('src/images/buttons/howtoplay.png'))
        self.backButton = CMUImage(
            PILImage.open('src/images/buttons/back.png'))
        self.normalModeButton = CMUImage(
            PILImage.open('src/images/buttons/normalmode.png'))
        self.mazeModeButton = CMUImage(
            PILImage.open('src/images/buttons/mazemode.png'))
        self.pauseButton = CMUImage(
            PILImage.open('src/images/buttons/pause.png').resize((40, 40)))
        self.playButton = CMUImage(
            PILImage.open('src/images/buttons/play.png').resize((70, 70)))
        self.leaderboardButton = CMUImage(
            PILImage.open('src/images/buttons/leaderboard.png'))
        self.startOverButton = CMUImage(
            PILImage.open('src/images/buttons/startover.png'))
