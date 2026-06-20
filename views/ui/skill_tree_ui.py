import pygame

from models.skills import SKILL_TREE_NODES
from config import HEIGHT, STAGE_TITLE_FONT_PATH, WIDTH


class SkillTreeUI:
    """Отображает дерево навыков и обрабатывает выбор улучшений."""
    def __init__(self):
        self.background = pygame.image.load("assets/images/skill_tree/tree.png").convert_alpha()
        lock_source = pygame.image.load("assets/images/skill_tree/lock.png").convert_alpha()
        self.lock_image = self._crop_lock_image(lock_source)
        self.dim_surface = self._create_dim_surface()
        self.star_counter_font = pygame.font.Font(STAGE_TITLE_FONT_PATH, 42)

        self.source_size = self.background.get_size()
        self.draw_rect = self._get_background_rect()
        self.background_scaled = pygame.transform.smoothscale(
            self.background,
            self.draw_rect.size
        )

        self.skills = SKILL_TREE_NODES

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

    def draw(self, surface, player=None):
        surface.blit(self.dim_surface, (0, 0))
        surface.blit(self.background_scaled, self.draw_rect)
        self._draw_star_counter(surface, player)

        for skill in self.skills:
            if player and player.has_skill(skill.skill_id):
                continue
            if skill.is_locked:
                self._draw_lock(surface, skill.icon_rect)

    def handle_click(self, mouse_pos, player):
        if not player:
            return False

        for skill in self.skills:
            if not self._scale_rect(skill.icon_rect).collidepoint(mouse_pos):
                continue
            if not self._can_unlock(skill, player):
                return False
            return player.unlock_skill(skill.skill_id, skill.cost)

        return False

    def _can_unlock(self, skill, player):
        if player.has_skill(skill.skill_id) or player.stars < skill.cost:
            return False

        return all(player.has_skill(dependency) for dependency in skill.dependencies)

    def _draw_star_counter(self, surface, player=None):
        counter_position = self._scale_point((150, 97))
        stars = player.stars if player else 0
        text_surface = self.star_counter_font.render(str(stars), True, (255, 255, 255))
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
