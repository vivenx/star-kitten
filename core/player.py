import pygame
import os
import re
from settings import (
    PLAYER_SPEED, PLAYER_MAX_HP, PLAYER_SIZE, PLAYER_COLLISION_HEIGHT_RATIO,
    PLAYER_ATTACK_COOLDOWN, DAMAGE_COOLDOWN_DEFAULT, COLOR_DAMAGE_FLASH
)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.sprites = {
            'right': [],
            'left': []
        }
        self.attack_sprites = {
            'right': [],
            'left': []
        }
        self.damage_sprites = {
            'right': [],
            'left': []
        }

        base_path = 'assets/images/sprites_player'

        default_sprite_path = os.path.join(base_path, 'default.png')
        self.default_image = pygame.image.load(default_sprite_path).convert_alpha()

        sprite_size = self.default_image.get_size()
        self.sprites['right'] = self._load_animation(os.path.join(base_path, 'right', 'walk'), sprite_size)
        self.sprites['left'] = self._load_animation(os.path.join(base_path, 'left', 'walk'), sprite_size)
        self.attack_sprites['right'] = self._load_animation(os.path.join(base_path, 'right', 'attack'), sprite_size)
        self.attack_sprites['left'] = self._load_animation(os.path.join(base_path, 'left', 'attack'), sprite_size)
        self.damage_sprites['right'] = self._load_animation(os.path.join(base_path, 'right', 'damage'), sprite_size)
        self.damage_sprites['left'] = self._load_animation(os.path.join(base_path, 'left', 'damage'), sprite_size)

        if not self.damage_sprites['right']:
            self.damage_sprites['right'] = [self.default_image]
        if not self.damage_sprites['left']:
            self.damage_sprites['left'] = [self.default_image]

        self.direction = 'right'
        self.current_frame = 0
        self.animation_speed = 5
        self.animation_counter = 0
        self.attack_animation_speed = 4
        self.attack_frame = 0
        self.attack_counter = 0
        self.attack_cooldown = 0.0
        self.attack_cooldown_max = PLAYER_ATTACK_COOLDOWN
        self.is_attacking = False
        self.damage_animation_speed = 5
        self.damage_frame = 0
        self.damage_animation_counter = 0
        self.is_damage_animating = False

        self.image = self.default_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


        self.speed = PLAYER_SPEED


        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)

        self.is_moving = False


        self.max_hp = PLAYER_MAX_HP
        self.hp = self.max_hp


        self.damage_cooldown = 0.0
        self.damage_cooldown_max = DAMAGE_COOLDOWN_DEFAULT
        self.invincible = False


        self.collision_height_ratio = PLAYER_COLLISION_HEIGHT_RATIO
        self._update_collision_rect()

    def _load_animation(self, folder_path, size=None):
        files = [
            file_name
            for file_name in os.listdir(folder_path)
            if file_name.lower().endswith('.png')
        ]
        files.sort(key=lambda file_name: (
            self._get_frame_number(file_name)
            if self._get_frame_number(file_name) is not None
            else 0,
            file_name
        ))

        sprites = []
        for file_name in files:
            sprite = pygame.image.load(os.path.join(folder_path, file_name)).convert_alpha()
            if size:
                sprite = pygame.transform.scale(sprite, size)
            sprites.append(sprite)
        return sprites

    def _get_frame_number(self, file_name):
        match = re.search(r'\((\d+)\)|(\d+)', file_name)
        if not match:
            return None
        return int(match.group(1) or match.group(2))

    def _update_collision_rect(self):
        collision_height = int(self.rect.height * self.collision_height_ratio)
        collision_y = self.rect.bottom - collision_height
        self.collision_rect = pygame.Rect(
            self.rect.left,
            collision_y,
            self.rect.width,
            collision_height
        )

    def get_collision_rect(self):
        self._update_collision_rect()
        return self.collision_rect

    def take_damage(self, damage):
        if self.invincible:
            return False

        self.hp -= damage
        self.start_damage_animation()
        if self.hp <= 0:
            self.hp = 0
            return True
        return False

    def start_damage_animation(self):
        self.is_damage_animating = True
        self.damage_frame = 0
        self.damage_animation_counter = 0
        self.image = self.damage_sprites[self.direction][self.damage_frame]

    def start_damage_cooldown(self):
        self.damage_cooldown = self.damage_cooldown_max
        self.invincible = True

    def update_cooldown(self, dt):
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
            if self.damage_cooldown <= 0:
                self.damage_cooldown = 0
                self.invincible = False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            if self.attack_cooldown < 0:
                self.attack_cooldown = 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def is_alive(self):
        return self.hp > 0

    def get_hp_percent(self):
        return self.hp / self.max_hp

    def update(self, dt):
        if self.is_damage_animating:
            self.damage_animation_counter += dt * 60
            if self.damage_animation_counter >= self.damage_animation_speed:
                self.damage_animation_counter = 0
                self.damage_frame += 1
                if self.damage_frame >= len(self.damage_sprites[self.direction]):
                    self.damage_frame = 0
                    self.is_damage_animating = False

            if self.is_damage_animating:
                self.image = self.damage_sprites[self.direction][self.damage_frame]
        elif self.is_attacking:
            self.attack_counter += dt * 60
            if self.attack_counter >= self.attack_animation_speed:
                self.attack_counter = 0
                self.attack_frame += 1
                if self.attack_frame >= len(self.attack_sprites[self.direction]):
                    self.attack_frame = 0
                    self.is_attacking = False

            if self.is_attacking:
                self.image = self.attack_sprites[self.direction][self.attack_frame]
        elif self.is_moving:
            self.animation_counter += dt * 60
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.sprites[self.direction])
                self.image = self.sprites[self.direction][self.current_frame]
        else:
            self.current_frame = 0
            self.image = self.default_image


        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)


        self._update_collision_rect()

    def start_attack(self, mouse_pos):
        if self.attack_cooldown > 0 or self.is_attacking:
            return False

        if mouse_pos[0] < self.get_collision_rect().centerx:
            self.direction = 'left'
        else:
            self.direction = 'right'

        self.attack_cooldown = self.attack_cooldown_max
        self.is_attacking = True
        self.attack_frame = 0
        self.attack_counter = 0
        self.image = self.attack_sprites[self.direction][self.attack_frame]
        return True

    def update_rect(self):
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)
        self._update_collision_rect()

    def move(self, dx, dy, dt):
        self.is_moving = False
        self.velocity = pygame.Vector2(0, 0)

        if dx != 0 or dy != 0:

            direction = pygame.Vector2(dx, dy).normalize()
            self.velocity = direction * self.speed
            self.is_moving = True


            if not self.is_attacking:
                if dx > 0:
                    self.direction = 'right'
                elif dx < 0:
                    self.direction = 'left'


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


        self._update_collision_rect()

    def set_position(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.rect.x = int(x)
        self.rect.y = int(y)

        self._update_collision_rect()

    def is_taking_damage_from_crystal(self):
        return not self.invincible
