"""Game orchestration: the state machine, wave manager, collision handling,
scoring and high-score persistence. ``Game.run()`` owns the main loop.
"""

import json
import os
import random

import pygame

import assets
import ui
from effects import Starfield, Effects
from enemy import spawn_enemy
from player import Player
from settings import (
    WIDTH, HEIGHT, FPS, TITLE, WHITE, UI_ACCENT, UI_GOOD, GOLD, UI_WARN,
    PLAYER_LIVES, PLAYER_DASH_COOLDOWN, WAVE_BASE_COUNT, WAVE_COUNT_GROWTH,
    WAVE_MAX_ONSCREEN, BOSS_EVERY, HIGHSCORE_FILE,
    STATE_MENU, STATE_PLAY, STATE_PAUSE, STATE_GAMEOVER,
)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.starfield = Starfield()
        self.effects = Effects()
        self.hud = ui.HUD()
        self.menu = ui.MenuScreen()
        self.gameover_screen = ui.GameOverScreen()

        self.high_score = self._load_highscore()
        self.state = STATE_MENU
        self.running = True
        self.new_high = False

        self._reset()

    # --- persistence ---------------------------------------------------------
    def _load_highscore(self):
        try:
            with open(HIGHSCORE_FILE) as fh:
                return int(json.load(fh).get("high_score", 0))
        except (OSError, ValueError, json.JSONDecodeError):
            return 0

    def _save_highscore(self):
        try:
            with open(HIGHSCORE_FILE, "w") as fh:
                json.dump({"high_score": self.high_score}, fh)
        except OSError as exc:
            print(f"[game] could not save high score: {exc}")

    # --- run state -----------------------------------------------------------
    def _reset(self):
        self.player = Player(WIDTH // 2, HEIGHT - 50)
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()

        self.score = 0
        self.lives = PLAYER_LIVES
        self.wave = 0
        self.pending = []          # queued enemy kinds for the current wave
        self.wave_banner_until = 0
        self.wave_break_until = 0  # short pause between waves
        self.player_alive = True
        self.respawn_at = 0
        self.new_high = False

    def _start_game(self):
        self._reset()
        self.state = STATE_PLAY
        self._start_wave()

    # --- waves ---------------------------------------------------------------
    def _start_wave(self):
        self.wave += 1
        count = WAVE_BASE_COUNT + (self.wave - 1) * WAVE_COUNT_GROWTH
        kinds = []
        is_boss = self.wave % BOSS_EVERY == 0
        if is_boss:
            kinds.append("boss")
            count = max(2, count // 2)
        for i in range(count):
            # Faster cats become more common in later waves.
            if self.wave >= 2 and random.random() < min(0.5, 0.12 * self.wave):
                kinds.append("fast")
            else:
                kinds.append("grunt")
        random.shuffle(kinds)
        self.pending = kinds
        self._spawn_from_queue()
        self.wave_banner_until = pygame.time.get_ticks() + 1600
        assets.play("wave", 0.6)

    def _spawn_from_queue(self):
        while self.pending and len(self.enemies) < WAVE_MAX_ONSCREEN:
            self.enemies.add(spawn_enemy(self.pending.pop(), self.wave))

    # --- events --------------------------------------------------------------
    def _handle_events(self):
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and self.state in (STATE_PLAY, STATE_PAUSE):
                    self.state = STATE_PAUSE if self.state == STATE_PLAY else STATE_PLAY
                elif event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAY:
                        self.state = STATE_PAUSE
                    elif self.state == STATE_MENU:
                        self.running = False
                    else:
                        self.state = STATE_MENU

            if self.state == STATE_MENU:
                if self.menu.play_btn.clicked(event):
                    self._start_game()
                elif self.menu.quit_btn.clicked(event):
                    self.running = False
            elif self.state == STATE_GAMEOVER:
                if self.gameover_screen.retry_btn.clicked(event):
                    self._start_game()
                elif self.gameover_screen.menu_btn.clicked(event):
                    self.state = STATE_MENU

        # Menu / game-over button hover animations.
        if self.state == STATE_MENU:
            self.menu.update(mouse)
        elif self.state == STATE_GAMEOVER:
            self.gameover_screen.update(mouse)

    # --- gameplay update -----------------------------------------------------
    def _update_play(self):
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # Player movement + fire (hold-to-fire).
        if self.player_alive:
            self.player.update(keys)
            if self.player.moving:
                self.effects.thruster(*self.player.thruster_pos)
            if keys[pygame.K_l] or keys[pygame.K_SPACE]:
                bullet = self.player.fire()
                if bullet:
                    self.player_bullets.add(bullet)
                    self.effects.sparks(*self.player.muzzle, UI_ACCENT, count=3)
                    assets.play("shoot", 0.5)
        elif now >= self.respawn_at:
            self.player_alive = True
            self.player.respawn()

        # Enemies.
        self.enemies.update()
        for enemy in self.enemies:
            for bullet in enemy.try_fire():
                self.enemy_bullets.add(bullet)
        self.player_bullets.update()
        self.enemy_bullets.update()

        self._handle_collisions()

        # Wave flow: refill from queue, advance when cleared.
        self._spawn_from_queue()
        if not self.enemies and not self.pending:
            if self.wave_break_until == 0:
                self.wave_break_until = now + 1200
            elif now >= self.wave_break_until:
                self.wave_break_until = 0
                self._start_wave()

    def _handle_collisions(self):
        # Player bullets -> enemies.
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets,
                                          False, True)
        for enemy, bullets in hits.items():
            dead = enemy.take_damage(sum(b.damage for b in bullets))
            self.effects.sparks(enemy.rect.centerx, enemy.rect.centery, WHITE)
            assets.play("hit", 0.35)
            if dead:
                enemy.kill()
                self.score += enemy.score
                self.effects.explosion(enemy.rect.centerx, enemy.rect.centery,
                                       enemy.color,
                                       count=30 if enemy.kind == "boss" else 20,
                                       speed=8 if enemy.kind == "boss" else 6)
                self.effects.floating_text(f"+{enemy.score}", enemy.rect.centerx,
                                           enemy.rect.top, GOLD)
                self.effects.shake(6 if enemy.kind == "boss" else 2)
                assets.play("explosion", 0.5 if enemy.kind == "boss" else 0.3)

        if not self.player_alive or self.player.invulnerable:
            return

        # Enemy bullets or bodies -> player.
        struck = pygame.sprite.spritecollide(self.player, self.enemy_bullets,
                                             True)
        rammed = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if struck or rammed:
            self._player_hit()

    def _player_hit(self):
        self.lives -= 1
        self.effects.explosion(self.player.rect.centerx, self.player.rect.centery,
                               UI_ACCENT, count=28, speed=7)
        self.effects.shake(12)
        self.player_alive = False
        if self.lives <= 0:
            self._end_game()
        else:
            assets.play("player_hit", 0.6)
            self.respawn_at = pygame.time.get_ticks() + 1200

    def _end_game(self):
        assets.play("gameover", 0.7)
        self.new_high = self.score > self.high_score
        if self.new_high:
            self.high_score = self.score
            self._save_highscore()
        self.state = STATE_GAMEOVER

    # --- draw ----------------------------------------------------------------
    def _draw_world(self, target):
        self.enemy_bullets.draw(target)
        self.player_bullets.draw(target)
        self.enemies.draw(target)
        if self.player_alive:
            target.blit(self.player.image, self.player.rect)
        self.effects.draw(target)

    def _draw(self):
        now = pygame.time.get_ticks()
        # Render the world to a buffer so screen-shake can offset it.
        world = self.screen
        ox, oy = (0, 0)

        self.starfield.draw(self.screen)

        if self.state in (STATE_PLAY, STATE_PAUSE, STATE_GAMEOVER):
            ox, oy = self.effects.offset if self.state == STATE_PLAY else (0, 0)
            if ox or oy:
                buf = pygame.Surface((WIDTH, HEIGHT))
                buf.blit(self.starfield._bg, (0, 0))
                self.starfield.draw(buf)
                self._draw_world(buf)
                self.screen.blit(buf, (ox, oy))
            else:
                self._draw_world(self.screen)

            dash_frac = min(1.0, (now - self.player.last_dash) / PLAYER_DASH_COOLDOWN)
            self.hud.draw(self.screen, self.score, self.wave, self.high_score,
                          self.lives, dash_frac)

            if now < self.wave_banner_until and self.state == STATE_PLAY:
                label = "BOSS WAVE" if self.wave % BOSS_EVERY == 0 else f"WAVE {self.wave}"
                color = UI_WARN if self.wave % BOSS_EVERY == 0 else UI_ACCENT
                ui.draw_text(self.screen, label, 60, WIDTH // 2, HEIGHT // 2,
                             color=color, glow=True)

        if self.state == STATE_MENU:
            self.menu.draw(self.screen, self.high_score)
        elif self.state == STATE_PAUSE:
            ui.draw_pause(self.screen)
        elif self.state == STATE_GAMEOVER:
            self.gameover_screen.draw(self.screen, self.score, self.high_score,
                                      self.wave, self.new_high)

        pygame.display.flip()

    # --- main loop -----------------------------------------------------------
    def run(self):
        while self.running:
            self._handle_events()
            self.starfield.update(1.5 if self.state == STATE_PLAY else 0.6)
            if self.state == STATE_PLAY:
                self._update_play()
                self.effects.update()
            self._draw()
            self.clock.tick(FPS)
