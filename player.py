"""The player's fighter jet.

Free-roam WASD movement with a short dash (LSHIFT) and hold-to-fire. Damage is
handled by the game via a lives system; the player itself only tracks dash
state, fire cooldown, and a brief invulnerability window after being hit.
"""

import pygame

import assets
from bullet import Bullet
from settings import (
    WIDTH, HEIGHT, PLAYER_SCALE, PLAYER_SPEED, PLAYER_DASH_SPEED,
    PLAYER_DASH_DURATION, PLAYER_DASH_COOLDOWN, PLAYER_FIRE_COOLDOWN,
    PLAYER_BULLET_SPEED, PLAYER_INVULN_TIME,
)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_image = assets.load_image("jet2.png", scale=PLAYER_SCALE)
        self.image = self.base_image
        self.rect = self.base_image.get_rect(midbottom=(x, y))
        self.pos = pygame.math.Vector2(x, y)

        self.speed = PLAYER_SPEED
        self.is_dashing = False
        self.dash_time = 0
        self.last_dash = -PLAYER_DASH_COOLDOWN

        self.last_bullet = 0
        self.fire_cooldown = PLAYER_FIRE_COOLDOWN

        self.invuln_until = 0
        self.moving = False

    # --- state helpers -------------------------------------------------------
    @property
    def invulnerable(self):
        return pygame.time.get_ticks() < self.invuln_until

    def grant_invuln(self, duration=PLAYER_INVULN_TIME):
        self.invuln_until = pygame.time.get_ticks() + duration

    def dash_ready(self):
        return pygame.time.get_ticks() - self.last_dash >= PLAYER_DASH_COOLDOWN

    def respawn(self):
        self.pos = pygame.math.Vector2(WIDTH // 2, HEIGHT - 50)
        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))
        self.grant_invuln()

    # --- update --------------------------------------------------------------
    def update(self, keys):
        now = pygame.time.get_ticks()
        speed = self.speed

        if self.is_dashing and now - self.dash_time > PLAYER_DASH_DURATION:
            self.is_dashing = False

        move = pygame.math.Vector2(
            (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT]),
            (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP]),
        )
        self.moving = move.length_squared() > 0

        if keys[pygame.K_LSHIFT] and self.dash_ready() and self.moving:
            self.is_dashing = True
            self.dash_time = now
            self.last_dash = now

        if self.is_dashing:
            speed = PLAYER_DASH_SPEED

        if self.moving:
            self.pos += move.normalize() * speed

        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        self.pos = pygame.math.Vector2(self.rect.midbottom)

        # Blink while invulnerable for readable feedback.
        if self.invulnerable and (now // 100) % 2 == 0:
            self.image = self.base_image.copy()
            self.image.set_alpha(90)
        else:
            self.image = self.base_image

    def fire(self):
        now = pygame.time.get_ticks()
        if now - self.last_bullet >= self.fire_cooldown:
            self.last_bullet = now
            return Bullet(self.rect.centerx, self.rect.top,
                          (0, -PLAYER_BULLET_SPEED), owner="player")
        return None

    @property
    def muzzle(self):
        return (self.rect.centerx, self.rect.top)

    @property
    def thruster_pos(self):
        return (self.rect.centerx, self.rect.bottom - 6)
