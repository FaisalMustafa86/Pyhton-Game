"""User-interface layer: text helpers, buttons, HUD and the full-screen
menu / pause / game-over overlays.
"""

import math

import pygame

import assets
from settings import (
    WIDTH, HEIGHT, WHITE, UI_ACCENT, UI_ACCENT_DIM, UI_WARN, UI_GOOD, GOLD,
    PLAYER_DASH_COOLDOWN,
)


def draw_text(surface, text, size, x, y, color=WHITE, center=True,
              shadow=True, glow=False):
    font = assets.font(size)
    if glow:
        glow_surf = font.render(text, True, UI_ACCENT_DIM)
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            r = glow_surf.get_rect()
            r.center = (x + dx, y + dy) if center else (x + glow_surf.get_width() // 2 + dx, y + dy)
            surface.blit(glow_surf, r)
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        r = shadow_surf.get_rect()
        if center:
            r.center = (x + 2, y + 2)
        else:
            r.topleft = (x + 2, y + 2)
        surface.blit(shadow_surf, r)
    label = font.render(text, True, color)
    r = label.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surface.blit(label, r)
    return r


class Button:
    def __init__(self, text, cx, cy, w=220, h=56, size=30,
                 color=UI_ACCENT, hover=UI_GOOD):
        self.text = text
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.size = size
        self.color = color
        self.hover_color = hover
        self.hovered = False
        self._pulse = 0.0

    def update(self, mouse_pos):
        was = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and not was:
            assets.play("ui", 0.5)
        self._pulse += 0.12

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        rect = self.rect.copy()
        if self.hovered:
            grow = int(4 + math.sin(self._pulse) * 2)
            rect.inflate_ip(grow, grow)
        # Panel
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((color[0], color[1], color[2], 40))
        surface.blit(panel, rect.topleft)
        pygame.draw.rect(surface, color, rect, width=2, border_radius=8)
        draw_text(surface, self.text, self.size, rect.centerx, rect.centery,
                  color=WHITE if self.hovered else color, shadow=True)


class HUD:
    def __init__(self):
        self.jet_icon = assets.load_image("jet2.png", scale=0.9)

    def draw(self, surface, score, wave, high_score, lives, dash_frac):
        # Top bar backdrop
        bar = pygame.Surface((WIDTH, 44), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 90))
        surface.blit(bar, (0, 0))

        draw_text(surface, f"SCORE {score}", 24, 16, 10, color=UI_ACCENT,
                  center=False)
        draw_text(surface, f"WAVE {wave}", 24, WIDTH // 2, 22, color=WHITE)
        # right-aligned high score
        hi = assets.font(20).render(f"HI {high_score}", True, GOLD)
        surface.blit(hi, (WIDTH - hi.get_width() - 16, 14))

        # Lives as jet icons (bottom-left)
        for i in range(lives):
            icon = self.jet_icon
            surface.blit(icon, (14 + i * (icon.get_width() + 6),
                                HEIGHT - icon.get_height() - 12))

        # Dash cooldown bar (bottom-right)
        bw, bh = 140, 10
        bx, by = WIDTH - bw - 16, HEIGHT - 22
        pygame.draw.rect(surface, UI_ACCENT_DIM, (bx, by, bw, bh), border_radius=4)
        fill = int(bw * dash_frac)
        col = UI_GOOD if dash_frac >= 1.0 else UI_ACCENT
        if fill > 0:
            pygame.draw.rect(surface, col, (bx, by, fill, bh), border_radius=4)
        draw_text(surface, "DASH", 14, bx - 6, by + bh // 2, color=col,
                  center=False)


def _overlay(surface, alpha=170):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((6, 4, 16, alpha))
    surface.blit(ov, (0, 0))


class MenuScreen:
    """Animated title screen with floating jet + cats."""

    def __init__(self):
        self.jet = assets.load_image("jet2.png", scale=2.6, rotate=0)
        self.cat1 = assets.load_image("enemy.png", scale=2.2)
        self.cat2 = assets.load_image("boss1.png", scale=2.2)
        self.play_btn = Button("PLAY", WIDTH // 2, 330, w=240)
        self.quit_btn = Button("QUIT", WIDTH // 2, 405, w=240, color=UI_WARN,
                               hover=UI_WARN)
        self.t = 0.0

    @property
    def buttons(self):
        return (self.play_btn, self.quit_btn)

    def update(self, mouse_pos):
        self.t += 0.03
        for b in self.buttons:
            b.update(mouse_pos)

    def draw(self, surface, high_score):
        _overlay(surface, 120)
        # Floating mascots
        surface.blit(self.cat1, (150 + math.sin(self.t) * 20, 150 + math.cos(self.t * 0.8) * 12))
        surface.blit(self.cat2, (WIDTH - 230 + math.cos(self.t) * 20, 160 + math.sin(self.t) * 14))
        jy = 120 + math.sin(self.t * 1.2) * 10
        surface.blit(self.jet, (WIDTH // 2 - self.jet.get_width() // 2, int(jy) - 40))

        draw_text(surface, "CAT INVASION", 74, WIDTH // 2, 240,
                  color=UI_ACCENT, glow=True)
        draw_text(surface, "defend the skies from the feline menace", 20,
                  WIDTH // 2, 285, color=WHITE)
        for b in self.buttons:
            b.draw(surface)
        draw_text(surface, f"HIGH SCORE  {high_score}", 22, WIDTH // 2, 470,
                  color=GOLD)
        draw_text(surface, "WASD move   L / SPACE fire   LSHIFT dash   P pause",
                  18, WIDTH // 2, 540, color=UI_ACCENT_DIM)


class GameOverScreen:
    def __init__(self):
        self.retry_btn = Button("RETRY", WIDTH // 2 - 130, 400, w=200)
        self.menu_btn = Button("MENU", WIDTH // 2 + 130, 400, w=200,
                               color=UI_WARN, hover=UI_WARN)
        self.t = 0.0

    @property
    def buttons(self):
        return (self.retry_btn, self.menu_btn)

    def update(self, mouse_pos):
        self.t += 0.05
        for b in self.buttons:
            b.update(mouse_pos)

    def draw(self, surface, score, high_score, wave, new_high):
        _overlay(surface, 190)
        draw_text(surface, "GAME OVER", 80, WIDTH // 2, 200, color=UI_WARN,
                  glow=True)
        draw_text(surface, f"SCORE  {score}", 34, WIDTH // 2, 285, color=WHITE)
        draw_text(surface, f"REACHED WAVE  {wave}", 24, WIDTH // 2, 325,
                  color=UI_ACCENT)
        if new_high:
            flash = GOLD if int(self.t * 4) % 2 == 0 else WHITE
            draw_text(surface, "NEW HIGH SCORE!", 30, WIDTH // 2, 360, color=flash)
        else:
            draw_text(surface, f"HIGH SCORE  {high_score}", 24, WIDTH // 2, 360,
                      color=GOLD)
        for b in self.buttons:
            b.draw(surface)


def draw_pause(surface):
    _overlay(surface, 150)
    draw_text(surface, "PAUSED", 70, WIDTH // 2, HEIGHT // 2 - 20,
              color=UI_ACCENT, glow=True)
    draw_text(surface, "press P to resume", 24, WIDTH // 2, HEIGHT // 2 + 40,
              color=WHITE)
