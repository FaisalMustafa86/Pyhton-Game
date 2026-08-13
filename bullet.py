"""Projectiles for both the player and the cats.

A single class handles every bullet; a velocity vector and an ``owner`` tag
(``"player"`` or ``"enemy"``) distinguish them, replacing the old duplicated
``Bullet`` / ``enemyBullet`` pair.
"""

import pygame

import assets
from settings import WIDTH, HEIGHT


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity, owner="player", damage=1, color=None):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.velocity = pygame.math.Vector2(velocity)

        base = assets.load_image("player bullet.png", size=(10, 26))
        if owner == "enemy":
            # Tint enemy bullets red so the player can read incoming danger.
            base = base.copy()
            base.fill((255, 80, 80, 255), special_flags=pygame.BLEND_RGBA_MULT)
        self.image = base
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)

    def update(self, keys=None):
        self.pos += self.velocity
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if (self.rect.bottom < -20 or self.rect.top > HEIGHT + 20
                or self.rect.right < -20 or self.rect.left > WIDTH + 20):
            self.kill()
