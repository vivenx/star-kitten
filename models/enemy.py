import random

import pygame

from settings import (
    ENEMY_ATTACK_COOLDOWN,
    ENEMY_COLLISION_WIDTH_RATIO,
    ENEMY_COLLISION_HEIGHT_RATIO,
    ENEMY_DAMAGE,
    ENEMY_DAMAGE_SCALE,
    ENEMY_HP_SCALE,
    ENEMY_MAX_HP,
    ENEMY_PATH_UPDATE_TIME,
    ENEMY_SIZE,
    ENEMY_SPEED,
    ENEMY_SPEED_SCALE,
)


class Enemy(pygame.sprite.Sprite):
    behavior_type = "melee_chase"

    def __init__(self, x, y, difficulty_multiplier=1.0):
        super().__init__()

        self.direction = "left"
        self.visual_action = None
        self.visual_action_id = 0

        self.rect = pygame.Rect(0, 0, ENEMY_SIZE[0], ENEMY_SIZE[1])
        self.rect.x = x
        self.rect.y = y

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.is_moving = False

        difficulty_bonus = max(0.0, difficulty_multiplier - 1.0)
        self.max_hp = int(ENEMY_MAX_HP * (1.0 + difficulty_bonus * ENEMY_HP_SCALE))
        self.current_hp = self.max_hp
        self.damage = int(ENEMY_DAMAGE * (1.0 + difficulty_bonus * ENEMY_DAMAGE_SCALE))
        self.speed = ENEMY_SPEED * (1.0 + difficulty_bonus * ENEMY_SPEED_SCALE)
        self.attack_cooldown = 0.0
        self.attack_cooldown_max = ENEMY_ATTACK_COOLDOWN

        self.path = []
        self.path_index = 0
        self.path_update_timer = random.uniform(0, ENEMY_PATH_UPDATE_TIME)
        self.path_update_time = ENEMY_PATH_UPDATE_TIME

        self.collision_height_ratio = ENEMY_COLLISION_HEIGHT_RATIO
        self.collision_width_ratio = ENEMY_COLLISION_WIDTH_RATIO
        self._update_collision_rect()

    def take_damage(self, damage):
        self.current_hp -= damage
        self.request_damage_visual()
        if self.current_hp <= 0:
            self.current_hp = 0
            return True
        return False

    def request_damage_visual(self):
        self._request_visual_action("damage")

    def is_alive(self):
        return self.current_hp > 0

    def get_collision_rect(self):
        self._update_collision_rect()
        return self.collision_rect

    def request_attack_visual(self, player):
        if player.get_collision_rect().centerx < self.get_collision_rect().centerx:
            self.direction = "left"
        else:
            self.direction = "right"

        self._request_visual_action("attack")

    def sync_rect(self):
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)
        self._update_collision_rect()

    def _request_visual_action(self, action):
        self.visual_action = action
        self.visual_action_id += 1

    def _update_collision_rect(self):
        collision_width = int(self.rect.width * self.collision_width_ratio)
        collision_height = int(self.rect.height * self.collision_height_ratio)
        collision_x = self.rect.centerx - collision_width // 2
        collision_y = self.rect.bottom - collision_height
        self.collision_rect = pygame.Rect(
            collision_x,
            collision_y,
            collision_width,
            collision_height
        )

