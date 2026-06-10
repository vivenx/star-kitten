import pygame

from settings import (
    STAGE_TITLE_FONT_PATH,
    XP_BAR_HEIGHT,
    XP_BAR_IMAGE_PATH,
    XP_BAR_LERP_SPEED,
    XP_BAR_WIDTH,
)


class XPBar:
    SOURCE_CROP_RECT = pygame.Rect(34, 159, 2114, 361)
    SOURCE_FILL_RECT = pygame.Rect(356, 128, 1615, 169)
    FILL_COLOR = (75, 210, 255)
    FILL_DARK_COLOR = (20, 38, 58)
    TEXT_COLOR = (235, 252, 255)
    SHADOW_COLOR = (10, 16, 32)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = XP_BAR_WIDTH
        self.height = XP_BAR_HEIGHT
        self.display_percent = 0.0
        self.image = self._load_image()
        self.fill_rect = self._scale_rect(self.SOURCE_FILL_RECT, self.SOURCE_CROP_RECT.size, self.image.get_size())
        self.font = pygame.font.Font(STAGE_TITLE_FONT_PATH, 16)
        self.level_font = pygame.font.Font(STAGE_TITLE_FONT_PATH, 10)

    def _load_image(self):
        image = pygame.image.load(XP_BAR_IMAGE_PATH)
        if pygame.display.get_surface():
            image = image.convert_alpha()
        image = image.subsurface(self.SOURCE_CROP_RECT).copy()
        return pygame.transform.smoothscale(image, (self.width, self.height))

    def _scale_rect(self, rect, source_size, target_size):
        scale_x = target_size[0] / source_size[0]
        scale_y = target_size[1] / source_size[1]
        return pygame.Rect(
            int(rect.x * scale_x),
            int(rect.y * scale_y),
            int(rect.width * scale_x),
            int(rect.height * scale_y),
        )

    def update(self, dt, player):
        required_xp = player.get_required_xp()
        target_percent = 0.0 if required_xp <= 0 else player.xp / required_xp
        lerp = min(1.0, XP_BAR_LERP_SPEED * dt)
        self.display_percent += (target_percent - self.display_percent) * lerp

    def draw(self, surface, player):
        required_xp = player.get_required_xp()
        percent = max(0.0, min(1.0, self.display_percent))
        image_rect = self.image.get_rect(topleft=(self.x, self.y))
        fill_rect = self.fill_rect.move(image_rect.topleft)
        fill_width = int(fill_rect.width * percent)

        pygame.draw.rect(surface, self.FILL_DARK_COLOR, fill_rect)
        if fill_width > 0:
            pygame.draw.rect(surface, self.FILL_COLOR, (fill_rect.x, fill_rect.y, fill_width, fill_rect.height))

        surface.blit(self.image, image_rect)
        self._draw_level(surface, image_rect, player.level)
        self._draw_value(surface, fill_rect, player.xp, required_xp)

    def _draw_level(self, surface, image_rect, level):
        text = f"Level {int(level)}"
        text_surface = self.level_font.render(text, True, self.TEXT_COLOR)
        shadow_surface = self.level_font.render(text, True, self.SHADOW_COLOR)
        text_rect = text_surface.get_rect(
            center=(image_rect.x + int(self.width * 0.087), image_rect.y + int(self.height * 0.5))
        )
        shadow_rect = text_rect.move(2, 2)
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)

    def _draw_value(self, surface, fill_rect, current_xp, required_xp):
        text = f"{int(current_xp)}/{int(required_xp)}"
        text_surface = self.font.render(text, True, self.TEXT_COLOR)
        shadow_surface = self.font.render(text, True, self.SHADOW_COLOR)
        text_rect = text_surface.get_rect(center=fill_rect.center)
        shadow_rect = text_rect.move(2, 2)
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)
