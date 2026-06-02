from dataclasses import dataclass, field

import pygame

from settings import HEIGHT, STAGE_TITLE_FONT_PATH, WIDTH, SKILL_LOCKED, SKILL_UNLOCKED


@dataclass(frozen=True)
class SkillNode:
    skill_id: str
    icon_rect: pygame.Rect
    state: str = SKILL_LOCKED
    cost: int = 0
    dependencies: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_locked(self):
        return self.state == SKILL_LOCKED


class SkillTreeUI:
    def __init__(self):
        self.background = pygame.image.load("assets/images/skill_tree/tree.png").convert_alpha()
        lock_source = pygame.image.load("assets/images/skill_tree/lock.png").convert_alpha()
        self.lock_image = self._crop_lock_image(lock_source)
        self.dim_surface = self._create_dim_surface()
        self.stars = 0
        self.star_counter_font = pygame.font.Font(STAGE_TITLE_FONT_PATH, 42)

        self.source_size = self.background.get_size()
        self.draw_rect = self._get_background_rect()
        self.background_scaled = pygame.transform.smoothscale(
            self.background,
            self.draw_rect.size
        )

        self.skills = self._create_test_skills()

    def _create_test_skills(self):
        return [
            SkillNode("attack_slash", pygame.Rect(62, 253, 158, 154), SKILL_LOCKED, cost=5),
            SkillNode(
                "attack_wave",
                pygame.Rect(62, 487, 158, 154),
                SKILL_LOCKED,
                cost=8,
                dependencies=("attack_slash",),
            ),
            SkillNode(
                "attack_double_hit",
                pygame.Rect(62, 747, 158, 154),
                SKILL_LOCKED,
                cost=12,
                dependencies=("attack_wave",),
            ),
            SkillNode("fairy_heal", pygame.Rect(559, 253, 158, 154), SKILL_LOCKED, cost=5),
            SkillNode(
                "fairy_cooldown",
                pygame.Rect(559, 489, 158, 154),
                SKILL_LOCKED,
                cost=8,
                dependencies=("fairy_heal",),
            ),
            SkillNode(
                "fairy_rescue",
                pygame.Rect(559, 747, 158, 154),
                SKILL_LOCKED,
                cost=12,
                dependencies=("fairy_cooldown",),
            ),
            SkillNode("defense_hp", pygame.Rect(1056, 282, 157, 177), SKILL_LOCKED, cost=5),
            SkillNode(
                "defense_shield",
                pygame.Rect(1056, 625, 157, 177),
                SKILL_LOCKED,
                cost=10,
                dependencies=("defense_hp",),
            ),
        ]

    def _crop_lock_image(self, lock_source):
        source_rect = lock_source.get_rect()
        crop_rect = pygame.Rect(570, 230, 400, 470).clip(source_rect)
        return lock_source.subsurface(crop_rect).copy()

    def _create_dim_surface(self):
        dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim_surface.fill((0, 0, 0, 150))
        return dim_surface

    def _get_background_rect(self):
        source_width, source_height = self.background.get_size()
        scale = min(WIDTH / source_width, HEIGHT / source_height)
        width = int(source_width * scale)
        height = int(source_height * scale)
        return pygame.Rect((WIDTH - width) // 2, (HEIGHT - height) // 2, width, height)

    def draw(self, surface):
        surface.blit(self.dim_surface, (0, 0))
        surface.blit(self.background_scaled, self.draw_rect)
        self._draw_star_counter(surface)

        for skill in self.skills:
            if skill.is_locked:
                self._draw_lock(surface, skill.icon_rect)

    def _draw_star_counter(self, surface):
        counter_position = self._scale_point((150, 97))
        text_surface = self.star_counter_font.render(str(self.stars), True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=counter_position)
        surface.blit(text_surface, text_rect)

    def _draw_lock(self, surface, source_icon_rect):
        icon_rect = self._scale_rect(source_icon_rect)
        lock_size = int(min(icon_rect.width, icon_rect.height) * 0.72)
        lock_image = pygame.transform.smoothscale(self.lock_image, (lock_size, lock_size))
        lock_rect = lock_image.get_rect(center=icon_rect.center)
        surface.blit(lock_image, lock_rect)

    def _scale_rect(self, source_rect):
        scale_x = self.draw_rect.width / self.source_size[0]
        scale_y = self.draw_rect.height / self.source_size[1]
        return pygame.Rect(
            self.draw_rect.x + int(source_rect.x * scale_x),
            self.draw_rect.y + int(source_rect.y * scale_y),
            int(source_rect.width * scale_x),
            int(source_rect.height * scale_y),
        )

    def _scale_point(self, source_point):
        scale_x = self.draw_rect.width / self.source_size[0]
        scale_y = self.draw_rect.height / self.source_size[1]
        return (
            self.draw_rect.x + int(source_point[0] * scale_x),
            self.draw_rect.y + int(source_point[1] * scale_y),
        )
