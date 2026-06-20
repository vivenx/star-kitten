import pygame

from models.enemy import Enemy
from config import (
    SLIME_ATTACK_COOLDOWN,
    SLIME_PROJECTILE_SIZE,
)


class SlimeProjectile:
    """Хранит положение и скорость снаряда слизня."""
    def __init__(self, center, velocity):
        self.position = pygame.Vector2(center)
        self.velocity = pygame.Vector2(velocity)
        self.rect = pygame.Rect(0, 0, SLIME_PROJECTILE_SIZE, SLIME_PROJECTILE_SIZE)
        self.rect.center = center
        self.alive = True


class Slime(Enemy):
    """Представляет дальнобойного противника, стреляющего снарядами."""
    behavior_type = "slime_ranged"
    visual_type = "slime"

    def __init__(self, x, y, difficulty_multiplier=1.0):
        super().__init__(x, y, difficulty_multiplier)
        self.projectiles = []
        self.attack_cooldown = SLIME_ATTACK_COOLDOWN * 0.5
        self.attack_cooldown_max = SLIME_ATTACK_COOLDOWN
