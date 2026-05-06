import pygame
import os
from settings import (
    PLAYER_SPEED, PLAYER_MAX_HP, PLAYER_SIZE, PLAYER_COLLISION_HEIGHT_RATIO,
    DAMAGE_COOLDOWN_DEFAULT, COLOR_DAMAGE_FLASH
)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.sprites = {
            'right': [],
            'left': [],
            'up': [],
            'down': []
        }

        base_path = 'assets/images/sprites_player'

        right_path = os.path.join(base_path, 'right')
        for i in range(1, 6):
            sprite = pygame.image.load(os.path.join(right_path, f'{i}_step.png')).convert_alpha()
            self.sprites['right'].append(sprite)

        left_path = os.path.join(base_path, 'left')
        for i in range(1, 6):
            sprite = pygame.image.load(os.path.join(left_path, f'{i}_step.png')).convert_alpha()
            self.sprites['left'].append(sprite)

        up_down_path = os.path.join(base_path, 'up_and_down')
        for i in range(1, 6):
            sprite = pygame.image.load(os.path.join(up_down_path, f'{i}_step.png')).convert_alpha()
            self.sprites['down'].append(sprite)
            self.sprites['up'].append(sprite)

        self.direction = 'down'
        self.current_frame = 0
        self.animation_speed = 5
        self.animation_counter = 0

        self.image = self.sprites[self.direction][self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # FPS independent movement - скорость в пикселях в секунду
        self.speed = PLAYER_SPEED

        # Вектор позиции для плавного движения
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)

        self.is_moving = False

        # Система характеристик
        self.max_hp = PLAYER_MAX_HP
        self.hp = self.max_hp

        # Cooldown для получения урона
        self.damage_cooldown = 0.0
        self.damage_cooldown_max = DAMAGE_COOLDOWN_DEFAULT
        self.invincible = False  # флаг неуязвимости во время cooldown

        # Collision rect только для нижней части тела (чтобы не биться "головой")
        self.collision_height_ratio = PLAYER_COLLISION_HEIGHT_RATIO
        self._update_collision_rect()

    def _update_collision_rect(self):
        """Обновление collision rect для нижней части тела."""
        collision_height = int(self.rect.height * self.collision_height_ratio)
        collision_y = self.rect.bottom - collision_height
        self.collision_rect = pygame.Rect(
            self.rect.left,
            collision_y,
            self.rect.width,
            collision_height
        )

    def get_collision_rect(self):
        """Возвращает collision rect для проверки коллизий."""
        self._update_collision_rect()
        return self.collision_rect

    def take_damage(self, damage):
        """Получить урон. Возвращает True если игрок умер."""
        if self.invincible:
            return False

        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            return True  # Игрок умер
        return False  # Игрок жив

    def start_damage_cooldown(self):
        """Запуск cooldown после получения урона."""
        self.damage_cooldown = self.damage_cooldown_max
        self.invincible = True

    def update_cooldown(self, dt):
        """Обновление cooldown урона."""
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
            if self.damage_cooldown <= 0:
                self.damage_cooldown = 0
                self.invincible = False

    def heal(self, amount):
        """Восстановить здоровье."""
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def is_alive(self):
        """Проверить, жив ли игрок."""
        return self.hp > 0

    def get_hp_percent(self):
        """Получить процент текущего здоровья."""
        return self.hp / self.max_hp

    def update(self, dt):
        """Обновление с delta time для FPS independent animation."""
        if self.is_moving:
            self.animation_counter += dt * 60  # нормализуем к 60 FPS
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.sprites[self.direction])
                self.image = self.sprites[self.direction][self.current_frame]
        else:
            self.current_frame = 3
            self.direction = 'down'
            self.image = self.sprites[self.direction][self.current_frame]

        # Синхронизируем rect с позицией (позицию меняет внешний код - game_scene)
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)

        # Обновляем collision rect после изменения позиции
        self._update_collision_rect()

    def update_rect(self):
        """Принудительное обновление rect и collision_rect без анимации."""
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)
        self._update_collision_rect()

    def move(self, dx, dy, dt):
        """Движение с delta time для FPS independent movement."""
        self.is_moving = False
        self.velocity = pygame.Vector2(0, 0)

        if dx != 0 or dy != 0:
            # Нормализуем диагональное движение
            direction = pygame.Vector2(dx, dy).normalize()
            self.velocity = direction * self.speed
            self.is_moving = True

            # Обновляем направление для анимации
            if dx > 0:
                self.direction = 'right'
            elif dx < 0:
                self.direction = 'left'
            elif dy > 0:
                self.direction = 'down'
            elif dy < 0:
                self.direction = 'up'

        # Ограничение по экрану
        screen_width, screen_height = pygame.display.get_surface().get_size()
        if self.rect.left < 0:
            self.rect.left = 0
            self.position.x = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
            self.position.x = screen_width - self.rect.width
        if self.rect.top < 0:
            self.rect.top = 0
            self.position.y = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.position.y = screen_height - self.rect.height

        # Обновляем collision rect после ограничения позиции
        self._update_collision_rect()

    def set_position(self, x, y):
        """Установка позиции игрока."""
        self.position = pygame.Vector2(x, y)
        self.rect.x = int(x)
        self.rect.y = int(y)
        # Обновляем collision rect после установки позиции
        self._update_collision_rect()

    def is_taking_damage_from_crystal(self):
        """Проверяет может ли игрок получить урон от кристалла сейчас."""
        return not self.invincible