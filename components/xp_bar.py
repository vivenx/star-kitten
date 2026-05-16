import pygame

from settings import XP_BAR_HEIGHT, XP_BAR_LERP_SPEED, XP_BAR_WIDTH


class XPBar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = XP_BAR_WIDTH
        self.height = XP_BAR_HEIGHT
        self.display_percent = 0.0
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)

    def update(self, dt, player):
        required_xp = player.get_required_xp()
        target_percent = 0.0 if required_xp <= 0 else player.xp / required_xp
        lerp = min(1.0, XP_BAR_LERP_SPEED * dt)
        self.display_percent += (target_percent - self.display_percent) * lerp

    def draw(self, surface, player):
        required_xp = player.get_required_xp()
        bar_rect = pygame.Rect(self.x, self.y + 34, self.width, self.height)
        fill_width = int(self.width * max(0.0, min(1.0, self.display_percent)))

        level_surface = self.font.render(f"Level {player.level}", True, (255, 255, 255))
        xp_label_surface = self.small_font.render("XP", True, (210, 235, 255))
        xp_value_surface = self.small_font.render(f"{player.xp} / {required_xp}", True, (255, 255, 255))

        surface.blit(level_surface, (self.x, self.y))
        surface.blit(xp_label_surface, (self.x, self.y + 22))

        pygame.draw.rect(surface, (18, 28, 42), bar_rect, border_radius=4)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
            pygame.draw.rect(surface, (75, 190, 255), fill_rect, border_radius=4)
        pygame.draw.rect(surface, (220, 240, 255), bar_rect, width=2, border_radius=4)

        value_rect = xp_value_surface.get_rect(midtop=(bar_rect.centerx, bar_rect.bottom + 4))
        surface.blit(xp_value_surface, value_rect)
