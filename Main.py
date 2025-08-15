import pygame
import sys
import ship
import bullet

pygame.init()
pygame.font.init()
#Constants

screenWidth = ship.screenWidth
screenHeight= ship.screenHeight
FPS=60
gameState = 1

#Color
white=(255,255,255)
black=(0,0,0)
skyBlue = (135,206,235)

gameScreen=pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption("Game")
gameClock = pygame.time.Clock()
player = ship.Player(screenWidth // 2, screenHeight)


projectiles = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
           if event.key == pygame.K_RETURN:
                bullet = player.fire()
                projectiles.add(bullet)     
           elif event.key == pygame.K_p:
                gameState = 2
                print("paused")

        #make KEYUP to un pause 
        #bullet bug on puase
        #pause is not drawn on screen
    
    keys = pygame.key.get_pressed()

    if gameState == 1:      
        all_sprites.update(keys)
        projectiles.update()
    if gameState == 2:
        font = pygame.font.SysFont('Arial', 36) 
        text_surface = font.render('PAUSED', True, black) 
    gameScreen.fill(skyBlue)  
    all_sprites.draw(gameScreen)   
    projectiles.draw(gameScreen)
    pygame.display.flip()

    gameClock.tick(60)



pygame.quit()
sys.exit()