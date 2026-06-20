import random

import pygame

from models.enemy import Enemy
from models.slime import Slime
from config import (
    CAVE_SLIME_BOSS_FIRST_ATTACK_DELAY,
    CAVE_SLIME_BOSS_MAX_HP,
    CAVE_SLIME_BOSS_SIZE,
    CAVE_SLIME_MINION_SIZE,
)


class CaveSlimeBoss(Enemy):
    """Представляет пещерного босса, создающего мини-слизней."""
    is_boss = True
    behavior_type = "cave_slime_boss"
    visual_type = "cave_slime_boss"

    def __init__(self, play_area, difficulty_multiplier=1.0):
        x = play_area.centerx - CAVE_SLIME_BOSS_SIZE[0] // 2
        y = play_area.centery - CAVE_SLIME_BOSS_SIZE[1] // 2
        super().__init__(x, y, difficulty_multiplier)
        self.rect = pygame.Rect(x, y, *CAVE_SLIME_BOSS_SIZE)
        self.position.update(x, y)
        self.max_hp = int(CAVE_SLIME_BOSS_MAX_HP * difficulty_multiplier)
        self.current_hp = self.max_hp
        self.speed = 0
        self.is_moving = False
        self.attack_timer = CAVE_SLIME_BOSS_FIRST_ATTACK_DELAY
        self.attack_visual_timer = 0.0
        self.summon_count = 0
        self._update_collision_rect()

    def resize_around_center(self, size):
        center = self.rect.center
        self.rect.size = size
        self.rect.center = center
        self.position.update(self.rect.topleft)
        self._update_collision_rect()


class MiniSlime(Slime):
    """Представляет уменьшенного слизня, создаваемого пещерным боссом."""
    is_summoned_minion = True

    def __init__(self, x, y, difficulty_multiplier=1.0):
        super().__init__(x, y, difficulty_multiplier)
        self.visual_type = f"mini_slime_{random.randint(1, 3)}"
        self.rect = pygame.Rect(x, y, *CAVE_SLIME_MINION_SIZE)
        self.position.update(x, y)
        self.max_hp = max(1, int(self.max_hp * 0.55))
        self.current_hp = self.max_hp
        self.damage = max(1, int(self.damage * 0.7))
        self.speed *= 1.15
        self._update_collision_rect()
