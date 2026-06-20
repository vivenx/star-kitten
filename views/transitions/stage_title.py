import pygame

from config import (
    HEIGHT,
    STAGE_TITLE_COLOR,
    STAGE_TITLE_FADE_TIME,
    STAGE_TITLE_FONT_PATH,
    STAGE_TITLE_FONT_SIZE,
    STAGE_TITLE_HOLD_TIME,
    STAGE_TITLE_SHADOW_COLOR,
    STAGE_TITLE_SUBTITLE_FONT_SIZE,
    WIDTH,
)


class StageTitle:
    """Показывает название и описание текущего этапа."""
    def __init__(self):
        self.title_font = pygame.font.Font(STAGE_TITLE_FONT_PATH, STAGE_TITLE_FONT_SIZE)
        self.subtitle_font = pygame.font.Font(STAGE_TITLE_FONT_PATH, STAGE_TITLE_SUBTITLE_FONT_SIZE)
        self.title = ""
        self.subtitle = ""
        self.timer = 0.0
        self.duration = self._get_default_duration()
        self.active = False

    def show(self, title, subtitle=""):
        self.title = title
        self.subtitle = subtitle
        self.timer = 0.0
        self.duration = self._get_default_duration()
        self.active = True

    def update(self, dt):
        if not self.active:
            return

        self.timer += dt
        if self.timer >= self.duration:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return

        alpha = self._get_alpha()
        if alpha <= 0:
            return

        title_surface = self.title_font.render(self.title, True, STAGE_TITLE_COLOR)
        shadow_surface = self.title_font.render(self.title, True, STAGE_TITLE_SHADOW_COLOR)
        title_surface.set_alpha(alpha)
        shadow_surface.set_alpha(alpha)

        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 36))
        shadow_rect = shadow_surface.get_rect(center=(WIDTH // 2 + 4, HEIGHT // 2 - 32))
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(title_surface, title_rect)

        if self.subtitle:
            subtitle_surface = self.subtitle_font.render(self.subtitle, True, STAGE_TITLE_COLOR)
            subtitle_shadow_surface = self.subtitle_font.render(self.subtitle, True, STAGE_TITLE_SHADOW_COLOR)
            subtitle_surface.set_alpha(alpha)
            subtitle_shadow_surface.set_alpha(alpha)

            subtitle_rect = subtitle_surface.get_rect(center=(WIDTH // 2, title_rect.bottom + 34))
            subtitle_shadow_rect = subtitle_shadow_surface.get_rect(
                center=(WIDTH // 2 + 3, title_rect.bottom + 37)
            )
            surface.blit(subtitle_shadow_surface, subtitle_shadow_rect)
            surface.blit(subtitle_surface, subtitle_rect)

    def _get_alpha(self):
        if self.timer < STAGE_TITLE_FADE_TIME:
            return int(255 * (self.timer / STAGE_TITLE_FADE_TIME))

        fade_out_start = STAGE_TITLE_FADE_TIME + STAGE_TITLE_HOLD_TIME
        if self.timer > fade_out_start:
            fade_progress = (self.timer - fade_out_start) / STAGE_TITLE_FADE_TIME
            return int(255 * max(0.0, 1.0 - fade_progress))

        return 255

    def _get_default_duration(self):
        return STAGE_TITLE_FADE_TIME * 2 + STAGE_TITLE_HOLD_TIME
