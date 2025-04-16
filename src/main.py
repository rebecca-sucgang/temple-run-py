from ursina import *
import random

app = Ursina()

# Player setup
player = Entity(model='cube', color=color.azure, scale=(1, 2, 1), position=(0, 1, 0))

# Road segments
roadSegments = []
for i in range(10):
    segment = Entity(model='cube', color=color.gray, scale=(5, 0.1, 10), position=(0, 0, i * 10))
    roadSegments.append(segment)

# Coins
coinList = []

def spawnCoin():
    x = random.choice([-1, 0, 1]) * 2
    z = player.z + 50
    coin = Entity(model='sphere', color=color.yellow, scale=0.5, position=(x, 1, z))
    coinList.append(coin)

# Spawn initial coins
for _ in range(5):
    spawnCoin()

# Update function
def update():
    player.z += time.dt * 5  # Move player forward

    # Move left/right
    if held_keys['a']:
        player.x -= time.dt * 5
    if held_keys['d']:
        player.x += time.dt * 5

    # Reposition road segments
    for segment in roadSegments:
        if segment.z + 10 < player.z:
            segment.z += 100

    # Reposition coins
    for coin in coinList:
        if coin.z < player.z - 5:
            coin.z += 100
            coin.x = random.choice([-1, 0, 1]) * 2

    # Check for coin collection
    for coin in coinList:
        if distance(player.position, coin.position) < 1:
            coin.disable()
            coinList.remove(coin)
            spawnCoin()

app.run()
