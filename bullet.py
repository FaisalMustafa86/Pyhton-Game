import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.image.load("/home/faisal/Documents/GitHub/Pyhton-Game/Assets/player bullet.png").convert_alpha()
        scaleWidth = self.image.get_width() // 4
        scaleHeight = self.image.get_height() // 1
        self.image = pygame.transform.scale(self.image, (scaleWidth, scaleHeight))
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = 10
        self.damage = 1

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        if self.rect.bottom < 0 or self.rect.top > 600:
            self.kill()