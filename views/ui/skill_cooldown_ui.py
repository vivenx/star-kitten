import math

import pygame

from settings import (
    DEFENSE_SHIELD_COOLDOWN,
    SKILL_COOLDOWN_ICON_SIZE,
    STAGE_TITLE_FONT_PATH,
    WIDTH,
)


class SkillCooldownUI:
    """Cooldown icons for the two active skill-branch effects."""

    def __init__(self):
        self.font = pygame.font.Font(STAGE_TITLE_FONT_PATH, 30)
        self.icons = {
            "fairy_heal": self._load_icon("assets/images/skill_tree/time_heal.png"),
            "defense_shield": self._load_icon("assets/images/skill_tree/time_shield.png"),
        }

    def _load_icon(self, path):
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(
            image, (SKILL_COOLDOWN_ICON_SIZE, SKILL_COOLDOWN_ICON_SIZE)
        )

    def draw(self, surface, player):
        entries = []
        if player.has_skill("fairy_heal"):
            entries.append(("fairy_heal", player.heal_cooldown, player.get_heal_cooldown_max()))
        if player.has_skill("defense_shield"):
            entries.append(("defense_shield", player.shield_cooldown, DEFENSE_SHIELD_COOLDOWN))

        margin = 18
        gap = 12
        for index, (skill_id, remaining, maximum) in enumerate(reversed(entries)):
            x = WIDTH - margin - SKILL_COOLDOWN_ICON_SIZE - index * (
                SKILL_COOLDOWN_ICON_SIZE + gap
            )
            rect = pygame.Rect(x, margin, SKILL_COOLDOWN_ICON_SIZE, SKILL_COOLDOWN_ICON_SIZE)
            surface.blit(self.icons[skill_id], rect)
            self._draw_cooldown(surface, rect, remaining, maximum)

    def _draw_cooldown(self, surface, rect, remaining, maximum):
        if remaining <= 0:
            return

        ratio = min(1.0, remaining / maximum) if maximum > 0 else 0.0
        overlay_height = round(rect.height * ratio)
        overlay = pygame.Surface((rect.width, overlay_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (rect.x, rect.bottom - overlay_height))

        text = self.font.render(str(math.ceil(remaining)), True, (255, 255, 255))
        shadow = self.font.render(str(math.ceil(remaining)), True, (10, 10, 10))
        text_rect = text.get_rect(center=rect.center)
        surface.blit(shadow, text_rect.move(2, 2))
        surface.blit(text, text_rect)
