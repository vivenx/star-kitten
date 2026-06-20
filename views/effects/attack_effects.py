import math

import pygame

from config import (
    ATTACK_WAVE_HEIGHT,
    ATTACK_WAVE_RANGE,
    ATTACK_WAVE_SPEED,
    ATTACK_WAVE_WIDTH,
)


class SlashEffect:
    """Отображает кратковременный визуальный след атаки игрока."""
    def __init__(self, attack_rect, direction, color=(255, 92, 50)):
        self.rect = attack_rect.copy()
        self.direction = direction
        self.color = color
        self.timer = 0.0
        self.duration = 0.16

    def update(self, dt):
        self.timer += dt

    def is_alive(self):
        return self.timer < self.duration

    def draw(self, surface):
        progress = min(1.0, self.timer / self.duration)
        alpha = int(220 * (1.0 - progress))
        if alpha <= 0:
            return

        effect_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        glow_color = (*self.color, alpha // 2)
        edge_color = (255, 236, 184, alpha)
        slash_rect = effect_surface.get_rect().inflate(-8, -12)
        start_angle = math.radians(210 if self.direction == "right" else -30)
        end_angle = math.radians(330 if self.direction == "right" else 150)

        pygame.draw.arc(effect_surface, glow_color, slash_rect, start_angle, end_angle, 14)
        pygame.draw.arc(effect_surface, edge_color, slash_rect.inflate(-18, -20), start_angle, end_angle, 5)

        spark_x = int(self.rect.width * (0.72 if self.direction == "right" else 0.28))
        spark_y = self.rect.height // 2
        for offset in (-28, 0, 28):
            pygame.draw.line(
                effect_surface,
                (255, 178, 66, alpha),
                (spark_x, spark_y),
                (spark_x + (22 if self.direction == "right" else -22), spark_y + offset),
                2,
            )

        surface.blit(effect_surface, self.rect)


class EnergyWaveEffect:
    """Отвечает за отрисовку энергетической волны."""
    def __init__(self, origin, direction, damage):
        self.position = pygame.Vector2(origin)
        self.start_x = self.position.x
        self.direction = direction
        self.damage = damage
        self.hit_enemy_ids = set()
        self.alive = True
        self.phase = 0.0

    @property
    def rect(self):
        rect = pygame.Rect(0, 0, ATTACK_WAVE_WIDTH, ATTACK_WAVE_HEIGHT)
        rect.center = (int(self.position.x), int(self.position.y))
        return rect

    def update(self, dt):
        if not self.alive:
            return

        sign = -1 if self.direction == "left" else 1
        self.position.x += ATTACK_WAVE_SPEED * sign * dt
        self.phase += dt * 12

        if abs(self.position.x - self.start_x) >= ATTACK_WAVE_RANGE:
            self.alive = False

    def is_alive(self):
        return self.alive

    def draw(self, surface):
        if not self.alive:
            return

        self.draw_wave(surface, self, self.phase)

    @staticmethod
    def draw_wave(surface, wave, phase):
        if not wave.is_alive():
            return

        rect = wave.rect
        effect_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pulse = int(24 * math.sin(phase))
        core = (255, 246, 210, 230)
        aura = (255, 74 + pulse, 42, 110)
        trail = (255, 130, 50, 120)

        pygame.draw.ellipse(effect_surface, aura, effect_surface.get_rect().inflate(-4, -10), 4)
        pygame.draw.arc(effect_surface, core, effect_surface.get_rect().inflate(-14, -24), -1.2, 1.2, 7)

        tail_x = 8 if wave.direction == "right" else rect.width - 8
        head_x = rect.width - 12 if wave.direction == "right" else 12
        for offset in (-30, -10, 12, 32):
            pygame.draw.line(
                effect_surface,
                trail,
                (tail_x, rect.height // 2 + offset),
                (head_x, rect.height // 2 + offset // 3),
                3,
            )

        surface.blit(effect_surface, rect)
