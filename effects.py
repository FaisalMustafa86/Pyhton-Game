"""Visual juice: parallax starfield, particles, explosions, floating text,
and a screen-shake helper. Kept dependency-free (pure pygame + random).
"""

import random

import pygame

import assets
from settings import WIDTH, HEIGHT, SPACE_TOP, SPACE_BOTTOM


class Starfield:
    """Three parallax layers of stars scrolling downward for a sense of flight."""

    def __init__(self):
        self._bg = self._make_gradient()
        self.layers = []
        for depth, (count, speed, size, bright) in enumerate([
            (60, 0.4, 1, 90),
            (40, 0.9, 2, 150),
            (20, 1.6, 2, 230),
        ]):
            stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), size,
                      bright + random.randint(-30, 30)] for _ in range(count)]
            self.layers.append((speed, stars))

    @staticmethod
    def _make_gradient():
        surf = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            color = [int(SPACE_TOP[i] + (SPACE_BOTTOM[i] - SPACE_TOP[i]) * t)
                     for i in range(3)]
            pygame.draw.line(surf, color, (0, y), (WIDTH, y))
        return surf

    def update(self, dt_scale=1.0):
        for speed, stars in self.layers:
            for star in stars:
                star[1] += speed * dt_scale
                if star[1] > HEIGHT:
                    star[1] = 0
                    star[0] = random.randint(0, WIDTH)

    def draw(self, surface):
        surface.blit(self._bg, (0, 0))
        for _, stars in self.layers:
            for x, y, size, bright in stars:
                b = max(0, min(255, bright))
                surface.fill((b, b, min(255, b + 20)),
                             (int(x), int(y), size, size))


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size", "gravity")

    def __init__(self, x, y, vx, vy, life, color, size, gravity=0.0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.96
        self.vy *= 0.96
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        t = self.life / self.max_life
        size = max(1, int(self.size * t))
        r, g, b = self.color
        fade = 0.4 + 0.6 * t
        surface.fill((int(r * fade), int(g * fade), int(b * fade)),
                     (int(self.x), int(self.y), size, size))


class FloatingText:
    def __init__(self, text, x, y, color, size=22):
        self.surf = assets.font(size).render(text, True, color)
        self.x, self.y = x, y
        self.life = 45
        self.max_life = 45

    def update(self):
        self.y -= 1.2
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        img = self.surf.copy()
        img.set_alpha(alpha)
        surface.blit(img, (self.x - img.get_width() // 2, int(self.y)))


class Effects:
    """Owns all transient visuals and the screen-shake offset."""

    def __init__(self):
        self.particles = []
        self.texts = []
        self._shake = 0.0

    def shake(self, amount):
        self._shake = max(self._shake, amount)

    @property
    def offset(self):
        if self._shake <= 0.1:
            return (0, 0)
        return (random.randint(-int(self._shake), int(self._shake)),
                random.randint(-int(self._shake), int(self._shake)))

    def explosion(self, x, y, color, count=22, speed=6, size=5):
        for _ in range(count):
            ang = random.uniform(0, 6.283)
            spd = random.uniform(1, speed)
            self.particles.append(Particle(
                x, y, spd * pygame.math.Vector2(1, 0).rotate_rad(ang).x,
                spd * pygame.math.Vector2(1, 0).rotate_rad(ang).y,
                random.randint(20, 40), color, random.randint(2, size)))

    def sparks(self, x, y, color, count=6):
        for _ in range(count):
            self.particles.append(Particle(
                x, y, random.uniform(-2, 2), random.uniform(-2, 2),
                random.randint(10, 20), color, random.randint(1, 3)))

    def thruster(self, x, y):
        self.particles.append(Particle(
            x + random.uniform(-3, 3), y, random.uniform(-0.6, 0.6),
            random.uniform(1.5, 3.0), random.randint(8, 16),
            random.choice([(120, 200, 255), (200, 230, 255), (90, 160, 255)]),
            random.randint(2, 4)))

    def floating_text(self, text, x, y, color, size=22):
        self.texts.append(FloatingText(text, x, y, color, size))

    def update(self):
        self._shake *= 0.85
        self.particles = [p for p in self.particles if p.update()]
        self.texts = [t for t in self.texts if t.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
        for t in self.texts:
            t.draw(surface)
