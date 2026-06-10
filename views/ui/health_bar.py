import pygame

from settings import HP_BAR_HEIGHT, HP_BAR_IMAGE_PATH, HP_BAR_WIDTH, STAGE_TITLE_FONT_PATH


class HealthBar:
    SOURCE_SIZE = (2112, 353)
    SOURCE_FILL_RECT = pygame.Rect(385, 121, 1510, 130)
    FILL_COLOR = (196, 28, 42)
    FILL_DARK_COLOR = (110, 12, 24)
    TEXT_COLOR = (255, 244, 218)
    SHADOW_COLOR = (32, 10, 10)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = HP_BAR_WIDTH
        self.height = HP_BAR_HEIGHT
        self.image = self._load_image()
        self.fill_rect = self._scale_rect(self.SOURCE_FILL_RECT, self.SOURCE_SIZE, self.image.get_size())
        self.font = pygame.font.Font(STAGE_TITLE_FONT_PATH, 16)

    def _load_image(self):
        image = pygame.image.load(HP_BAR_IMAGE_PATH)
        if pygame.display.get_surface():
            image = image.convert_alpha()
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

    def draw(self, surface, current_hp, max_hp):
        percent = 0.0 if max_hp <= 0 else max(0.0, min(1.0, current_hp / max_hp))
        image_rect = self.image.get_rect(topleft=(self.x, self.y))
        fill_rect = self.fill_rect.move(image_rect.topleft)
        fill_width = int(fill_rect.width * percent)

        pygame.draw.rect(surface, self.FILL_DARK_COLOR, fill_rect)
        if fill_width > 0:
            pygame.draw.rect(surface, self.FILL_COLOR, (fill_rect.x, fill_rect.y, fill_width, fill_rect.height))

        surface.blit(self.image, image_rect)
        self._draw_value(surface, fill_rect, current_hp, max_hp)

    def _draw_value(self, surface, fill_rect, current_hp, max_hp):
        text = f"{int(current_hp)}/{int(max_hp)}"
        text_surface = self.font.render(text, True, self.TEXT_COLOR)
        shadow_surface = self.font.render(text, True, self.SHADOW_COLOR)
        text_rect = text_surface.get_rect(center=fill_rect.center)
        shadow_rect = text_rect.move(2, 2)
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)
