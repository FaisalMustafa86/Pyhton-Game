import pygame
import sys
import ship
from enemy import Enemy
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.font.init()


screenWidth = ship.screenWidth
screenHeight = ship.screenHeight
FPS = 60
score = 0
health = 3

gameState = 3
playState = 1
pauseState = 2
menuState = 3
deathState = 4

enemyx = random.randint(50,850)
enemyy = random.randint(50,550)

skyBlue = (135, 206, 235)
black = (0,0,0)
white = (255,255,255)

gameScreen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Cat Invasion")
gameClock = pygame.time.Clock()

player = ship.Player(screenWidth // 2, screenHeight - 50)
player_alive = True
respawn_time = 2000
death_time = 0

enemy1 = Enemy(enemyx, enemyy, random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)]))

shootSound = pygame.mixer.Sound("/home/faisal/Documents/GitHub/Pyhton-Game/Assets/shoot.wav")
shootSound.set_volume(0.4)
bossMusic =  pygame.mixer.music.load("/home/faisal/Documents/GitHub/Pyhton-Game/Assets/bgMusic.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)


menuShip = pygame.image.load("/home/faisal/Documents/GitHub/Pyhton-Game/Assets/jet2.png").convert_alpha()
menuShip = pygame.transform .scale(menuShip,(200,200))
menuShip = pygame.transform.rotate(menuShip, 50)

menuCat =  pygame.image.load("/home/faisal/Documents/GitHub/Pyhton-Game/Assets/enemy.png").convert_alpha()
menuCat = pygame.transform.scale(menuCat,(100,100))
menuCat= pygame.transform.rotate(menuCat,10)

menuBullet = pygame.image.load("/home/faisal/Documents/GitHub/Pyhton-Game/Assets/player bullet.png")
menuBullet = pygame.transform.scale(menuBullet,(10,40))
menuBullet = pygame.transform.rotate(menuBullet,51)

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


playButtonRect = pygame.Rect(700,200,130,50)
exitButtonRect = pygame.Rect(700,300,130,50)
retryButtonRect = pygame.Rect(700,200,130,50)

  

running = True
while running:
    
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():

        mouseX,mouseY=pygame.mouse.get_pos()

        if event.type == pygame.QUIT:
            running = False

        if exitButtonRect.collidepoint((mouseX,mouseY)):
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = False

        if playButtonRect.collidepoint((mouseX,mouseY)):
            if event.type == pygame.MOUSEBUTTONDOWN:
                gameState = playState
        
            elif event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_l and player_alive:
                    bullet_obj = player.fire()
                    if bullet_obj:
                        projectiles.add(bullet_obj)
                        all_sprites.add(bullet_obj)
                        shootSound.play()
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

        if current_time - last_shot > enemyShootCooldown:
            for enemy in enemies:
                bullet_obj = enemy.fire()
                if bullet_obj:
                    enemy_projectiles.add(bullet_obj)
                    all_sprites.add(bullet_obj)
                    shootSound.play()
            last_shot = current_time

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

                    health -= 1

                if health == 0:
                    gameState = deathState
                    health =3
                    score =0

    gameScreen.fill(skyBlue)
    all_sprites.draw(gameScreen)
    drawText(gameScreen, "SCORE: " + str(score), 30 , 820,25)
    drawText(gameScreen, "HEALTH: " + str(health), 30, 820, 55)
    

    if gameState == pauseState:
        drawText(gameScreen, "PAUSED", 50, screenWidth // 2, screenHeight // 2)
        

    if gameState == menuState:
        gameScreen.fill(skyBlue)
        pygame.draw.rect(gameScreen, white, playButtonRect)
        pygame.draw.rect(gameScreen, white, exitButtonRect)

        drawText (gameScreen, "PLAY",45,765,220)
        drawText (gameScreen, "Exit",45,765,320)
        drawText (gameScreen, "CAT INVASION", 100, 450,100 )

        gameScreen.blit(menuShip,(400,300))
        gameScreen.blit(menuCat,(100,140))
        gameScreen.blit(menuBullet,(340,290))

    if gameState == deathState:
        gameScreen.fill(skyBlue)
        pygame.draw.rect(gameScreen, white, retryButtonRect)
        pygame.draw.rect(gameScreen, white, exitButtonRect)

        drawText (gameScreen, "RETRY",45,765,220)
        drawText (gameScreen, "Exit",45,765,320)
        drawText (gameScreen, "YOU DIED", 100, 450,100 )  

        gameScreen.blit(menuShip,(400,300))
        gameScreen.blit(menuCat,(100,140))
        gameScreen.blit(menuBullet,(340,290))      

    pygame.display.flip()
    gameClock.tick(FPS)

pygame.quit()
sys.exit()