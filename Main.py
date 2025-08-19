import pygame
import sys
import ship
from enemy import Enemy
import random

pygame.init()
pygame.font.init()

screenWidth = ship.screenWidth
screenHeight = ship.screenHeight
FPS = 60
score = 0
deaths = 0

gameState = 1
playState = 1
pauseState = 2

enemyx = random.randint(50,850)
enemyy = random.randint(50,550)

skyBlue = (135, 206, 235)

gameScreen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Game")
gameClock = pygame.time.Clock()

player = ship.Player(screenWidth // 2, screenHeight - 50)
player_alive = True
respawn_time = 2000
death_time = 0

enemy1 = Enemy(enemyx, enemyy, random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)]))

projectiles = pygame.sprite.Group()
enemy_projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemies.add(enemy1)
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(enemy1)

def drawText(surface, text, size, x, y, color=(10,50,101)):
    font = pygame.font.SysFont("binaryCHRBRK", size)
    label = font.render(text, True, color)
    rect = label.get_rect(center=(x, y))
    surface.blit(label, rect)

enemyShootCooldown = 300
last_shot = 0

running = True
while running:
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l and player_alive:
                bullet_obj = player.fire()
                if bullet_obj:
                    projectiles.add(bullet_obj)
                    all_sprites.add(bullet_obj)
            elif event.key == pygame.K_p:
                gameState = pauseState if gameState == playState else playState

    if gameState == playState:
        if player_alive:
            all_sprites.update(keys)
        else:
            if current_time - death_time >= respawn_time:
                player_alive = True
                player.pos = pygame.math.Vector2(screenWidth // 2, screenHeight - 50)
                player.rect.midbottom = (int(player.pos.x), int(player.pos.y))
                all_sprites.add(player)

        projectiles.update()
        enemy_projectiles.update()

        hits = pygame.sprite.groupcollide(enemies, projectiles, False, True)
        for enemy_hit in hits:
            enemy_hit.health -= 1
            if enemy_hit.health <= 0:
                enemy_hit.kill()
                score +=1
               
                enemyx = random.randint(50,850)
                enemyy = random.randint(50,550)
                  
                newEnemy = Enemy(enemyx, enemyy, random.choice([(1,0), (-1,0), (0,1), (0,-1)]))
                enemies.add(newEnemy)
                all_sprites.add(newEnemy) 

        player_hits = pygame.sprite.groupcollide(pygame.sprite.Group(player), enemy_projectiles, False, True)
        for player_sprite, bullets in player_hits.items():
            if player_alive:
                player_sprite.health -= len(bullets)
                if player_sprite.health <= 0:
                    player_sprite.kill()
                    player_alive = False
                    death_time = current_time
                    
                    deaths += 1

    if gameState == playState:
        if current_time - last_shot > enemyShootCooldown:
            for enemy in enemies:
                bullet_obj = enemy.fire()
                if bullet_obj:
                    enemy_projectiles.add(bullet_obj)
                    all_sprites.add(bullet_obj)
            last_shot = current_time

    gameScreen.fill(skyBlue)
    all_sprites.draw(gameScreen)
    drawText(gameScreen, "SCORE: " + str(score), 30 , 820,25)
    drawText(gameScreen, "DEATHS: " + str(deaths), 30, 820, 55)

    if gameState == pauseState:
        drawText(gameScreen, "PAUSED", 50, screenWidth // 2, screenHeight // 2)

    pygame.display.flip()
    gameClock.tick(FPS)

pygame.quit()
sys.exit()
