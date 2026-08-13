"""The invading cats.

Three flavours, all sharing one class via a per-kind config table:

* ``grunt`` – the classic yellow cat, bounces and takes the odd potshot.
* ``fast``  – a smaller purple cat, quicker and more erratic.
* ``boss``  – a big armoured cat that fans out spread shots (boss waves only).

Movement keeps the original free-roam "bounce around the arena" feel, with a
little sine wobble added for life, and cats are kept in the upper play area so
the player's zone at the bottom stays fair.
"""

import math
import random

import pygame

import assets
from bullet import Bullet
from settings import (
    WIDTH, HEIGHT, ENEMY_BASE_SPEED, ENEMY_BULLET_SPEED, ENEMY_FIRE_COOLDOWN,
    SCORE_GRUNT, SCORE_FAST, SCORE_BOSS, UI_WARN, CAT_TINT,
)

# Cats roam the upper portion of the screen.
CAT_FLOOR = int(HEIGHT * 0.72)

KINDS = {
    "grunt": dict(sprite="enemy.png", scale=1.6, health=2, speed_mult=1.0,
                  score=SCORE_GRUNT, fire_mult=1.0, shots=1, color=CAT_TINT),
    "fast":  dict(sprite="boss1.png", scale=1.3, health=1, speed_mult=1.7,
                  score=SCORE_FAST, fire_mult=1.2, shots=1, color=(210, 130, 255)),
    "boss":  dict(sprite="boss1.png", scale=4.5, health=30, speed_mult=0.7,
                  score=SCORE_BOSS, fire_mult=1.8, shots=5, color=UI_WARN),
}


class Enemy(pygame.sprite.Sprite):
    def __init__(self, kind, x, y, direction, wave=1):
        super().__init__()
        cfg = KINDS[kind]
        self.kind = kind
        self.cfg = cfg
        self.color = cfg["color"]

        self.base_image = self._scaled(cfg["sprite"], cfg["scale"])
        self.image = self.base_image
        self.rect = self.base_image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)

        # Difficulty scales gently with the wave number.
        wave_boost = 1.0 + (wave - 1) * 0.06
        self.speed = ENEMY_BASE_SPEED * cfg["speed_mult"] * wave_boost
        self.direction = pygame.math.Vector2(direction)
        if self.direction.length_squared() == 0:
            self.direction = pygame.math.Vector2(1, 0)
        self.direction = self.direction.normalize()

        self.max_health = cfg["health"]
        self.health = cfg["health"]
        self.shots = cfg["shots"]
        self.score = cfg["score"]

        self.fire_cooldown = ENEMY_FIRE_COOLDOWN / cfg["fire_mult"] / wave_boost
        # Randomize first shot so a wave doesn't fire in unison.
        self.last_bullet = pygame.time.get_ticks() + random.randint(0, 1200)

        self.flash_frames = 0
        self._wobble = random.uniform(0, math.tau)

    @staticmethod
    def _scaled(sprite, scale):
        w, h = assets.load_image(sprite).get_size()
        return assets.load_image(sprite, size=(int(w * scale), int(h * scale)))

    # --- combat --------------------------------------------------------------
    def take_damage(self, amount):
        self.health -= amount
        self.flash_frames = 4
        return self.health <= 0

    @property
    def health_frac(self):
        return max(0.0, self.health / self.max_health)

    # --- update --------------------------------------------------------------
    def update(self, keys=None):
        self._wobble += 0.05
        wobble = math.sin(self._wobble) * 0.4
        self.pos += self.direction * self.speed
        self.pos.x += wobble

        # Bounce inside the cats' arena.
        if self.rect.left <= 0 and self.direction.x < 0:
            self.direction.x *= -1
        elif self.rect.right >= WIDTH and self.direction.x > 0:
            self.direction.x *= -1
        if self.rect.top <= 0 and self.direction.y < 0:
            self.direction.y *= -1
        elif self.rect.bottom >= CAT_FLOOR and self.direction.y > 0:
            self.direction.y *= -1

        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, CAT_FLOOR))
        self.pos = pygame.math.Vector2(self.rect.center)

        if self.flash_frames > 0:
            self.flash_frames -= 1
            self.image = assets.tinted_copy(self.base_image, (255, 255, 255))
        else:
            self.image = self.base_image

    def try_fire(self):
        now = pygame.time.get_ticks()
        if now - self.last_bullet < self.fire_cooldown:
            return []
        self.last_bullet = now
        return self._make_bullets()

    def _make_bullets(self):
        bullets = []
        cx, by = self.rect.centerx, self.rect.bottom
        if self.shots == 1:
            bullets.append(Bullet(cx, by, (0, ENEMY_BULLET_SPEED), owner="enemy"))
        else:
            spread = 50  # total fan angle in degrees
            for i in range(self.shots):
                t = i / (self.shots - 1) - 0.5
                vel = pygame.math.Vector2(0, ENEMY_BULLET_SPEED).rotate(t * spread)
                bullets.append(Bullet(cx, by, vel, owner="enemy"))
        return bullets


def random_direction():
    return random.choice([(1, 0.4), (-1, 0.4), (1, -0.4), (-1, -0.4),
                          (0.6, 1), (-0.6, 1)])


def spawn_enemy(kind, wave):
    x = random.randint(60, WIDTH - 60)
    y = random.randint(50, int(CAT_FLOOR * 0.6))
    return Enemy(kind, x, y, random_direction(), wave=wave)
