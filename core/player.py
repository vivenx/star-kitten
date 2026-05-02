import pygame
import os


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

        self.speed = 5

        self.is_moving = False

        # Система характеристик
        self.max_hp = 100
        self.hp = self.max_hp

    def take_damage(self, damage):
        """Получить урон"""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            return True  # Игрок умер
        return False  # Игрок жив

    def heal(self, amount):
        """Восстановить здоровье"""
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def is_alive(self):
        """Проверить, жив ли игрок"""
        return self.hp > 0

    def get_hp_percent(self):
        """Получить процент текущего здоровья"""
        return self.hp / self.max_hp

    def update(self):
        if self.is_moving:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.sprites[self.direction])
                self.image = self.sprites[self.direction][self.current_frame]
        else:
            self.current_frame = 3
            self.direction = 'down'
            self.image = self.sprites[self.direction][self.current_frame]

    def move(self, dx, dy):
        self.is_moving = False

        if dx > 0:
            self.direction = 'right'
            self.rect.x += self.speed
            self.is_moving = True
        elif dx < 0:
            self.direction = 'left'
            self.rect.x -= self.speed
            self.is_moving = True

        if dy > 0:
            self.direction = 'down'
            self.rect.y += self.speed
            self.is_moving = True
        elif dy < 0:
            self.direction = 'up'
            self.rect.y -= self.speed
            self.is_moving = True

        screen_width, screen_height = pygame.display.get_surface().get_size()
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height