import pygame
import sys

pygame.init()

#Constants

screenWidth = 800
screenHeight= 600
FPS=60

#Color
white=(255,255,255)
black=(0,0,0)
skyBlue = (135,206,235)

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load("/home/faisal/Projects/Python_Game_1/Assets/player.png").convert_alpha()
        scaleWidth = self.image.get_width()*4
        scaleHeight= self.image.get_height()*4
        self.image = pygame.transform.scale(self.image, (scaleWidth, scaleHeight))
        self.rect=self.image.get_rect()
        self.pos=pygame.math.Vector2(x,y)
        self.speed=4
        self.rect.midbottom=self.pos
        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))
       



    def update(self,keys):
        if keys[pygame.K_w]:
            self.pos.y-=self.speed
        if keys[pygame.K_s]:
            self.pos.y+=self.speed
        if keys[pygame.K_a]:
            self.pos.x-=self.speed
        if keys[pygame.K_d]:
            self.pos.x+=self.speed

        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))

        screen_rect = pygame.Rect(0, 0, 800, 600)
        self.rect.clamp_ip(screen_rect)
        self.pos = pygame.math.Vector2(self.rect.midbottom)


 

gameScreen=pygame.display.set_mode((screenWidth,screenHeight))
gameClock = pygame.time.Clock()

player = Player(100, 100)
player = Player(screenWidth // 2, screenHeight)

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