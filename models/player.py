import pygame
from config import (
    PLAYER_SPEED, PLAYER_SIZE, PLAYER_MAX_HP, PLAYER_COLLISION_HEIGHT_RATIO,
    PLAYER_ATTACK_COOLDOWN, DAMAGE_COOLDOWN_DEFAULT,
    PLAYER_ATTACK_DAMAGE, BASE_REQUIRED_XP, XP_PER_LEVEL,
    HP_PER_LEVEL, DAMAGE_PER_LEVEL,
    FAIRY_HEAL_AMOUNT, FAIRY_HEAL_COOLDOWN, FAIRY_HEAL_FAST_COOLDOWN,
    FAIRY_RESCUE_HP_THRESHOLD, DEFENSE_HP_BONUS, DEFENSE_SHIELD_COOLDOWN,
)


class Player(pygame.sprite.Sprite):
    """Хранит состояние игрока и реализует его основные игровые действия."""
    def __init__(self, x, y):
        super().__init__()

        self.direction = 'right'
        self.visual_action = None
        self.visual_action_id = 0
        self.attack_cooldown = 0.0
        self.attack_cooldown_max = PLAYER_ATTACK_COOLDOWN

        self.rect = pygame.Rect(0, 0, PLAYER_SIZE[0], PLAYER_SIZE[1])
        self.rect.x = x
        self.rect.y = y


        self.speed = PLAYER_SPEED


        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)

        self.is_moving = False


        self.max_hp = PLAYER_MAX_HP
        self.hp = self.max_hp
        self.attack_damage = PLAYER_ATTACK_DAMAGE
        self.level = 1
        self.xp = 0
        self.stars = 500
        self.unlocked_skills = set()
        self.heal_cooldown = 0.0
        self.shield_cooldown = 0.0


        self.damage_cooldown = 0.0
        self.damage_cooldown_max = DAMAGE_COOLDOWN_DEFAULT
        self.invincible = False


        self.collision_height_ratio = PLAYER_COLLISION_HEIGHT_RATIO
        self._update_collision_rect()

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

        if self.has_skill("defense_shield") and self.shield_cooldown <= 0:
            self.shield_cooldown = DEFENSE_SHIELD_COOLDOWN
            return False

        self.hp -= damage
        self.request_damage_visual()
        if self.hp <= 0:
            self.hp = 0
            return True
        self._try_rescue()
        return False

    def request_damage_visual(self):
        self._request_visual_action("damage")

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

        self.heal_cooldown = max(0.0, self.heal_cooldown - dt)
        self.shield_cooldown = max(0.0, self.shield_cooldown - dt)

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def use_heal_skill(self):
        if (
            not self.has_skill("fairy_heal")
            or self.heal_cooldown > 0
            or self.hp <= 0
            or self.hp >= self.max_hp
        ):
            return False

        self.heal(FAIRY_HEAL_AMOUNT)
        self.heal_cooldown = self.get_heal_cooldown_max()
        return True

    def get_heal_cooldown_max(self):
        if self.has_skill("fairy_cooldown"):
            return FAIRY_HEAL_FAST_COOLDOWN
        return FAIRY_HEAL_COOLDOWN

    def _try_rescue(self):
        if (
            self.has_skill("fairy_rescue")
            and self.heal_cooldown <= 0
            and 0 < self.hp <= self.max_hp * FAIRY_RESCUE_HP_THRESHOLD
        ):
            self.use_heal_skill()

    def get_required_xp(self):
        return BASE_REQUIRED_XP + self.level * XP_PER_LEVEL

    def add_xp(self, amount):
        if amount <= 0:
            return 0

        levels_gained = 0
        self.xp += amount

        while self.xp >= self.get_required_xp():
            self.xp -= self.get_required_xp()
            self.level_up()
            levels_gained += 1

        return levels_gained

    def add_stars(self, amount):
        if amount <= 0:
            return 0

        self.stars += amount
        return amount

    def has_skill(self, skill_id):
        return skill_id in self.unlocked_skills

    def unlock_skill(self, skill_id, cost):
        if self.has_skill(skill_id) or self.stars < cost:
            return False

        self.stars -= cost
        self.unlocked_skills.add(skill_id)
        if skill_id == "defense_hp":
            self.max_hp += DEFENSE_HP_BONUS
            self.hp += DEFENSE_HP_BONUS
        return True

    def get_progress_snapshot(self):
        return {
            "level": self.level,
            "xp": self.xp,
            "stars": self.stars,
            "max_hp": self.max_hp,
            "attack_damage": self.attack_damage,
            "unlocked_skills": tuple(sorted(self.unlocked_skills)),
        }

    def restore_progress_snapshot(self, snapshot):
        if not snapshot:
            return

        self.level = snapshot["level"]
        self.xp = snapshot["xp"]
        self.stars = snapshot.get("stars", 0)
        self.max_hp = snapshot["max_hp"]
        self.attack_damage = snapshot["attack_damage"]
        self.unlocked_skills = set(snapshot.get("unlocked_skills", ()))
        self.hp = min(self.hp, self.max_hp)

    def level_up(self):
        self.level += 1
        self.max_hp += HP_PER_LEVEL
        self.attack_damage += DAMAGE_PER_LEVEL
        self.hp = self.max_hp

    def is_alive(self):
        return self.hp > 0

    def get_hp_percent(self):
        return self.hp / self.max_hp

    def update(self, dt):
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)
        self._update_collision_rect()

    def start_attack(self, mouse_pos):
        if self.attack_cooldown > 0:
            return False

        if mouse_pos[0] < self.get_collision_rect().centerx:
            self.direction = 'left'
        else:
            self.direction = 'right'

        self.attack_cooldown = self.attack_cooldown_max
        self._request_visual_action("attack")
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

    def _request_visual_action(self, action):
        self.visual_action = action
        self.visual_action_id += 1
