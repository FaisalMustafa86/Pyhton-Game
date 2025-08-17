import pygame
import sys
import ship
import bullet
import enemy
import random

pygame.init()
pygame.font.init()

screenWidth = ship.screenWidth
screenHeight = ship.screenHeight
FPS = 60

gameState = 1
playState = 1
pauseState = 2

enemyx = random.randint(0,900)
enemyy = random.randint(30,100)

skyBlue = (135, 206, 235)

gameScreen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Game")
gameClock = pygame.time.Clock()

player = ship.Player(screenWidth // 2, screenHeight - 50)
enemy1 = enemy.Enemy(enemyx, enemyy)


projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemies.add(enemy1)
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(enemy1)

def drawText(surface, text, size, x, y, color=(255,255,255)):
    font = pygame.font.SysFont("binaryCHRBRK", size)
    label = font.render(text, True, color)
    rect = label.get_rect(center=(x, y))
    surface.blit(label, rect)

running = True
while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                bullet_obj = player.fire()
                if bullet_obj:
                    projectiles.add(bullet_obj)
            elif event.key == pygame.K_p:
                gameState = pauseState if gameState == playState else playState

    if gameState == playState:
        all_sprites.update(keys)
        projectiles.update()

        hits = pygame.sprite.groupcollide(enemies, projectiles, False, True)
        for enemy_hit in hits:
            enemy_hit.health -= 1
            if enemy_hit.health <= 0:
                enemy_hit.kill()

    gameScreen.fill(skyBlue)
    all_sprites.draw(gameScreen)
    projectiles.draw(gameScreen)

    if gameState == pauseState:
        drawText(gameScreen, "PAUSED", 50, screenWidth // 2, screenHeight // 2)

    pygame.display.flip()
    gameClock.tick(FPS)

pygame.quit()
sys.exit()
