import pygame
from bullet import Bullet

screenWidth = 900
screenHeight = 600

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load("/home/faisal/Documents/GitHub/Pyhton-Game/Assets/jet.png").convert_alpha()
        scaleWidth = self.image.get_width()*3
        scaleHeight= self.image.get_height()*3
        self.image = pygame.transform.scale(self.image, (scaleWidth, scaleHeight))
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)



        self.health = 3
        self.speed = 5
        self.dashSpeed = 15
        self.isDashing = False
        self.dashTime = 0
        self.dashDuration = 200
        self.canDash = True

        self.lastBullet = 0
        self.bulletCooldown = 300

        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))

    def update(self, keys):
        currentSpeed = self.speed
        if self.isDashing and pygame.time.get_ticks() - self.dashTime > self.dashDuration:
            self.isDashing = False

        if keys[pygame.K_LSHIFT] and self.canDash:
            if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]:
                self.isDashing = True
                self.dashTime = pygame.time.get_ticks()
                self.canDash = False
        if not keys[pygame.K_LSHIFT]:
            self.canDash = True

        if self.isDashing:
            currentSpeed = self.dashSpeed

        if keys[pygame.K_w]:
            self.pos.y -= currentSpeed
        if keys[pygame.K_s]:
            self.pos.y += currentSpeed
        if keys[pygame.K_a]:
            self.pos.x -= currentSpeed
        if keys[pygame.K_d]:
            self.pos.x += currentSpeed


        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))
        self.rect.clamp_ip(pygame.Rect(0,0,screenWidth,screenHeight))
        self.pos = pygame.math.Vector2(self.rect.midbottom)

    def fire(self):
        currentTime = pygame.time.get_ticks()
        if currentTime - self.lastBullet >= self.bulletCooldown:
            self.lastBullet = currentTime
            return Bullet(self.rect.centerx, self.rect.top, (0, -1))
        return None
