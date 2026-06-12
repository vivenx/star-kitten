import pygame

from models.enemy import Enemy
from settings import (
    BOSS_FIRST_ATTACK_DELAY,
    BOSS_MAX_HP,
    BOSS_ORB_SIZE,
    BOSS_SIZE,
)


class BossOrb:
    def __init__(self, center, velocity):
        self.position = pygame.Vector2(center)
        self.velocity = pygame.Vector2(velocity)
        self.rect = pygame.Rect(0, 0, BOSS_ORB_SIZE, BOSS_ORB_SIZE)
        self.rect.center = center
        self.alive = True

class BossSpike:
    WARNING_TIME = 0.55
    ACTIVE_TIME = 0.7
    SIZE = (70, 100)

    def __init__(self, center, variant):
        self.rect = pygame.Rect(0, 0, *self.SIZE)
        self.rect.midbottom = center
        self.variant = variant
        self.age = 0.0
        self.alive = True
        self.has_hit = False

    @property
    def frame_index(self):
        if self.age < self.WARNING_TIME:
            return 0
        progress = (self.age - self.WARNING_TIME) / self.ACTIVE_TIME
        return min(2, 1 + int(progress * 2))

    @property
    def is_dangerous(self):
        return self.WARNING_TIME <= self.age < self.WARNING_TIME + self.ACTIVE_TIME

class Boss(Enemy):
    is_boss = True
    behavior_type = "forest_boss"

    def __init__(self, play_area, difficulty_multiplier=1.0):
        center = play_area.center
        x = center[0] - BOSS_SIZE[0] // 2
        y = center[1] - BOSS_SIZE[1] // 2
        super().__init__(x, y, difficulty_multiplier)
        self.rect = pygame.Rect(x, y, *BOSS_SIZE)
        self.position.update(x, y)
        self.max_hp = int(BOSS_MAX_HP * difficulty_multiplier)
        self.current_hp = self.max_hp
        self.speed = 0
        self.is_moving = False
        self.attack_timer = BOSS_FIRST_ATTACK_DELAY
        self.attack_visual_timer = 0.0
        self.attack_number = 0
        self.orbs = []
        self.spikes = []
        self._update_collision_rect()
