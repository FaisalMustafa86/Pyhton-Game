import pygame
from bullet import Bullet

screenWidth = 900
screenHeight = 600

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("/home/faisal/Documents/GitHub/Pyhton-Game/Assets/enemy1.png").convert_alpha()
        scaleWidth = self.image.get_width()*4
        scaleHeight = self.image.get_height()*4
        self.image = pygame.transform.scale(self.image, (scaleWidth, scaleHeight))
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)

        self.health = 1
        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))

    def update(self, keys=None):
        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))

        

    def fire(self):
        currentTime = pygame.time.get_ticks()
        if currentTime - self.lastBullet >= self.bulletCooldown:
            self.lastBullet = currentTime
            return Bullet(self.rect.centerx, self.rect.top, (0, -1))
        return None
