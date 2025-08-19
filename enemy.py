import pygame
from enemyBullet import enemyBullet

screenWidth = 900
screenHeight = 600

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y,direction):
        super().__init__()
        self.image = pygame.image.load("/home/faisal/Documents/GitHub/Pyhton-Game/Assets/enemy1.png").convert_alpha()
        scaleWidth = self.image.get_width()*4
        scaleHeight = self.image.get_height()*4
        self.image = pygame.transform.scale(self.image, (scaleWidth, scaleHeight))
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.speed = 3
        self.direction = pygame.math.Vector2(direction)

        self.lastBullet = 0
        self.bulletCooldown = 600

        self.health = 1

        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))

    def update(self, keys=None):
        self.pos += self.direction * self.speed


        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))
        self.rect.clamp_ip(pygame.Rect(0,0,screenWidth,screenHeight))
        self.pos = pygame.math.Vector2(self.rect.midbottom)


        if self.rect.left <= 0 or self.rect.right >= screenWidth:
            self.direction.x *= -1

        if self.rect.top <= 0 or self.rect.bottom >= screenHeight:
            self.direction.y *= -1

    
    def fire(self):
        currentTime = pygame.time.get_ticks()
        if currentTime - self.lastBullet >= self.bulletCooldown:
            self.lastBullet = currentTime
            return enemyBullet(self.rect.centerx, self.rect.top, (0, -1))
        return None
