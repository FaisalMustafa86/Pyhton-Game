import pygame
import sys
import ship

pygame.init()

#Constants

screenWidth = ship.screenWidth
screenHeight= ship.screenHeight
FPS=60


#Color
white=(255,255,255)
black=(0,0,0)
skyBlue = (135,206,235)

gameScreen=pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption("Game")
gameClock = pygame.time.Clock()
player = ship.Player(screenWidth // 2, screenHeight)

all_sprites = pygame.sprite.Group()
all_sprites.add(player)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    all_sprites.update(keys)

    gameScreen.fill(skyBlue)  
    all_sprites.draw(gameScreen)   
    pygame.display.flip()

    gameClock.tick(60)



pygame.quit()
sys.exit()