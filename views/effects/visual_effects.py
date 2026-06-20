import pygame

from config import (
    DAMAGE_NUMBER_DURATION,
    DAMAGE_NUMBER_FONT_SIZE,
    DAMAGE_NUMBER_RISE_SPEED,
    HEIGHT,
    STAGE_CLEAR_MESSAGE_COLOR,
    STAGE_CLEAR_MESSAGE_FADE_TIME,
    STAGE_CLEAR_MESSAGE_FONT_SIZE,
    STAGE_CLEAR_MESSAGE_HOLD_TIME,
    STAGE_CLEAR_MESSAGE_SHADOW_COLOR,
    STAGE_TITLE_FONT_PATH,
    WIDTH,
)


class DamageNumber:
    """Отображает всплывающее и постепенно исчезающее число урона."""
    def __init__(self, x, y, amount, color):
        self.position = pygame.Vector2(x, y)
        self.amount = amount
        self.color = color
        self.timer = 0.0
        self.duration = DAMAGE_NUMBER_DURATION
        self.font = pygame.font.Font(None, DAMAGE_NUMBER_FONT_SIZE)

    def update(self, dt):
        self.timer += dt
        self.position.y -= DAMAGE_NUMBER_RISE_SPEED * dt

    def is_alive(self):
        return self.timer < self.duration

    def draw(self, surface):
        alpha = int(255 * max(0.0, 1.0 - self.timer / self.duration))
        text_surface = self.font.render(str(self.amount), True, self.color)
        shadow_surface = self.font.render(str(self.amount), True, (15, 15, 20))
        text_surface.set_alpha(alpha)
        shadow_surface.set_alpha(alpha)

        text_rect = text_surface.get_rect(center=(int(self.position.x), int(self.position.y)))
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)


class StageClearMessage:
    """Отображает сообщение об успешном прохождении этапа."""
    def __init__(self):
        self.font = pygame.font.Font(STAGE_TITLE_FONT_PATH, STAGE_CLEAR_MESSAGE_FONT_SIZE)
        self.text = "Этап зачищен!"
        self.timer = 0.0
        self.duration = STAGE_CLEAR_MESSAGE_FADE_TIME * 2 + STAGE_CLEAR_MESSAGE_HOLD_TIME
        self.active = False

    def show(self):
        self.timer = 0.0
        self.active = True

    def reset(self):
        self.timer = 0.0
        self.active = False

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

        text_surface = self.font.render(self.text, True, STAGE_CLEAR_MESSAGE_COLOR)
        shadow_surface = self.font.render(self.text, True, STAGE_CLEAR_MESSAGE_SHADOW_COLOR)
        text_surface.set_alpha(alpha)
        shadow_surface.set_alpha(alpha)

        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        shadow_rect = shadow_surface.get_rect(center=(WIDTH // 2 + 4, HEIGHT // 2 + 4))
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)

    def _get_alpha(self):
        if self.timer < STAGE_CLEAR_MESSAGE_FADE_TIME:
            return int(255 * (self.timer / STAGE_CLEAR_MESSAGE_FADE_TIME))

        fade_out_start = STAGE_CLEAR_MESSAGE_FADE_TIME + STAGE_CLEAR_MESSAGE_HOLD_TIME
        if self.timer > fade_out_start:
            fade_progress = (self.timer - fade_out_start) / STAGE_CLEAR_MESSAGE_FADE_TIME
            return int(255 * max(0.0, 1.0 - fade_progress))

        return 255
