import os
import random

import pygame

from settings import (
    ENEMY_ATTACK_COOLDOWN,
    ENEMY_COLLISION_WIDTH_RATIO,
    ENEMY_COLLISION_HEIGHT_RATIO,
    ENEMY_DAMAGE,
    ENEMY_MAX_HP,
    ENEMY_PATH_UPDATE_TIME,
    ENEMY_SIZE,
    ENEMY_SPEED,
)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.sprites = {
            "right": [],
            "left": [],
        }
        self._load_sprites()

        self.direction = "left"
        self.current_frame = 0
        self.animation_speed = 8
        self.animation_counter = random.uniform(0, self.animation_speed)

        self.image = self.sprites[self.direction][self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.is_moving = False

        self.max_hp = ENEMY_MAX_HP
        self.current_hp = self.max_hp
        self.damage = ENEMY_DAMAGE
        self.speed = ENEMY_SPEED
        self.attack_cooldown = 0.0
        self.attack_cooldown_max = ENEMY_ATTACK_COOLDOWN

        self.path = []
        self.path_index = 0
        self.path_update_timer = random.uniform(0, ENEMY_PATH_UPDATE_TIME)
        self.path_update_time = ENEMY_PATH_UPDATE_TIME

        self.collision_height_ratio = ENEMY_COLLISION_HEIGHT_RATIO
        self.collision_width_ratio = ENEMY_COLLISION_WIDTH_RATIO
        self._update_collision_rect()

    def _load_sprites(self):
        base_path = "assets/images/forest/enemies/skeleton"

        right_path = os.path.join(base_path, "right", "walk")
        for i in range(1, 7):
            sprite = pygame.image.load(os.path.join(right_path, f"sprite({i}).png")).convert_alpha()
            self.sprites["right"].append(pygame.transform.scale(sprite, ENEMY_SIZE))

        left_path = os.path.join(base_path, "left", "walk")
        for i in range(1, 7):
            sprite = pygame.image.load(os.path.join(left_path, f"left({i}).png")).convert_alpha()
            self.sprites["left"].append(pygame.transform.scale(sprite, ENEMY_SIZE))

    def update(self, dt, player, pathfinder, solid_rects, enemies):
        if not self.is_alive():
            return False

        self._update_attack_cooldown(dt)
        self._update_path(dt, player, pathfinder)
        self._move_along_path(dt, solid_rects, enemies)
        player_died = self._attack_player(player)
        self._update_animation(dt)
        self._sync_rect()
        return player_died

    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.current_hp = 0
            return True
        return False

    def is_alive(self):
        return self.current_hp > 0

    def get_collision_rect(self):
        self._update_collision_rect()
        return self.collision_rect

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self._draw_health_bar(surface)

    def _update_path(self, dt, player, pathfinder):
        self.path_update_timer -= dt
        if self.path_update_timer > 0:
            return

        self.path_update_timer = self.path_update_time

        new_path = pathfinder.find_path(
            self.get_collision_rect().center,
            player.get_collision_rect().center
        )

        if new_path:
            self.path = new_path
            self.path_index = 1 if len(self.path) > 1 else 0

    def _move_along_path(self, dt, solid_rects, enemies):
        self.is_moving = False
        self.velocity.update(0, 0)

        if not self.path or self.path_index >= len(self.path):
            return

        target = self.path[self.path_index]
        direction = target - pygame.Vector2(self.get_collision_rect().center)

        if direction.length() < 5:
            self.path_index += 1
            return

        direction = direction.normalize()
        self.velocity = direction * self.speed

        if self.velocity.x > 0:
            self.direction = "right"
        elif self.velocity.x < 0:
            self.direction = "left"

        moved = False
        moved = self._move_axis(self.velocity.x * dt, 0, solid_rects, enemies) or moved
        moved = self._move_axis(0, self.velocity.y * dt, solid_rects, enemies) or moved
        self.is_moving = moved

    def _move_axis(self, dx, dy, solid_rects, enemies):
        if dx == 0 and dy == 0:
            return False

        old_position = self.position.copy()
        self.position.x += dx
        self.position.y += dy
        self._sync_rect()

        if self._has_collision(solid_rects, enemies):
            self.position = old_position
            self._sync_rect()
            return False

        return True

    def _has_collision(self, solid_rects, enemies):
        collision_rect = self.get_collision_rect()

        for rect in solid_rects:
            if collision_rect.colliderect(rect):
                return True

        for enemy in enemies:
            if enemy is self or not enemy.is_alive():
                continue

            if collision_rect.colliderect(enemy.get_collision_rect()):
                return True

        return False

    def _attack_player(self, player):
        if self.attack_cooldown > 0:
            return False

        if not self.get_collision_rect().colliderect(player.get_collision_rect()):
            return False

        died = player.take_damage(self.damage)
        player.start_damage_cooldown()
        self.attack_cooldown = self.attack_cooldown_max
        return died

    def _update_attack_cooldown(self, dt):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            if self.attack_cooldown < 0:
                self.attack_cooldown = 0

    def _update_animation(self, dt):
        if self.is_moving:
            self.animation_counter += dt * 60
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.sprites[self.direction])
        else:
            self.current_frame = 0

        self.image = self.sprites[self.direction][self.current_frame]

    def _sync_rect(self):
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)
        self._update_collision_rect()

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

    def _draw_health_bar(self, surface):
        if self.current_hp >= self.max_hp:
            return

        bar_width = self.rect.width
        bar_height = 5
        x = self.rect.left
        y = self.rect.top - 8
        hp_percent = self.current_hp / self.max_hp

        pygame.draw.rect(surface, (60, 20, 20), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, (180, 40, 40), (x, y, int(bar_width * hp_percent), bar_height))
