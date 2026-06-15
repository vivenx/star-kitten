import math
import random

import pygame

from models.cave_slime_boss import MiniSlime
from settings import (
    BOSS_ATTACK_ANIMATION_DURATION,
    CAVE_SLIME_BOSS_ATTACK_COUNT,
    CAVE_SLIME_BOSS_ATTACK_INTERVAL,
    CAVE_SLIME_BOSS_MINIONS_PER_ATTACK,
    CAVE_SLIME_BOSS_MAX_HP,
    CAVE_SLIME_BOSS_MIN_SIZE,
    CAVE_SLIME_BOSS_SHRINK_FACTOR,
)


class CaveSlimeBossBehaviorSystem:
    def update(self, boss, dt, player, pathfinder, solid_rects, enemies, play_area):
        if not boss.is_alive():
            return False

        boss.direction = "left" if player.get_collision_rect().centerx < boss.rect.centerx else "right"
        boss.attack_visual_timer = max(0.0, boss.attack_visual_timer - dt)
        if boss.summon_count >= CAVE_SLIME_BOSS_ATTACK_COUNT:
            return False

        boss.attack_timer -= dt
        if boss.attack_timer <= 0:
            self.start_attack(boss, player, enemies, play_area, solid_rects)
            boss.attack_timer = CAVE_SLIME_BOSS_ATTACK_INTERVAL
        return False

    def start_attack(self, boss, player, enemies, play_area, solid_rects=()):
        if boss.summon_count >= CAVE_SLIME_BOSS_ATTACK_COUNT:
            return []

        boss.request_attack_visual(player)
        boss.attack_visual_timer = BOSS_ATTACK_ANIMATION_DURATION
        spawned = self._spawn_minions(boss, enemies, play_area, solid_rects)
        boss.summon_count += 1
        self._shrink(boss)
        return spawned

    @staticmethod
    def _spawn_minions(boss, enemies, play_area, solid_rects):
        spawned = []
        origin = pygame.Vector2(boss.rect.center)
        for index in range(CAVE_SLIME_BOSS_MINIONS_PER_ATTACK):
            angle = math.tau * index / CAVE_SLIME_BOSS_MINIONS_PER_ATTACK + random.uniform(-0.3, 0.3)
            radius = random.randint(100, 180)
            point = origin + pygame.Vector2(math.cos(angle), math.sin(angle)) * radius
            minion = MiniSlime(point.x, point.y, boss.max_hp / CAVE_SLIME_BOSS_MAX_HP)
            minion.rect.clamp_ip(play_area)
            minion.position.update(minion.rect.topleft)
            if any(minion.get_collision_rect().colliderect(rect) for rect in solid_rects):
                minion.rect.center = origin
                minion.position.update(minion.rect.topleft)
            minion.wave_index = getattr(boss, "wave_index", 0)
            enemies.append(minion)
            spawned.append(minion)
        return spawned

    @staticmethod
    def _shrink(boss):
        width = max(CAVE_SLIME_BOSS_MIN_SIZE[0], round(boss.rect.width * CAVE_SLIME_BOSS_SHRINK_FACTOR))
        height = max(CAVE_SLIME_BOSS_MIN_SIZE[1], round(boss.rect.height * CAVE_SLIME_BOSS_SHRINK_FACTOR))
        boss.resize_around_center((width, height))
