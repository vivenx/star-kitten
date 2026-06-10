import unittest

import pygame

from models.orbs.xp_orb import XPOrb
from views.ui.xp_bar import XPBar
from settings import XP_BAR_LERP_SPEED, XP_BAR_WIDTH


class DummyPlayer:
    def __init__(self, xp=0, required_xp=100):
        self.xp = xp
        self.required_xp = required_xp
        self.level = 1
        self.collision_rect = pygame.Rect(0, 0, 20, 20)

    def get_required_xp(self):
        return self.required_xp

    def get_collision_rect(self):
        return self.collision_rect


class XPComponentsTest(unittest.TestCase):
    def test_xp_bar_interpolates_toward_player_xp_percent(self):
        player = DummyPlayer(xp=50, required_xp=100)
        bar = XPBar(0, 0)

        bar.update(0.05, player)

        self.assertEqual(bar.display_percent, 0.5 * XP_BAR_LERP_SPEED * 0.05)

    def test_xp_bar_clamps_drawn_fill_width_for_large_xp(self):
        player = DummyPlayer(xp=150, required_xp=100)
        bar = XPBar(0, 0)

        bar.update(1.0, player)

        self.assertEqual(bar.display_percent, 1.5)

        surface = pygame.Surface((XP_BAR_WIDTH + 20, 100))
        bar.draw(surface, player)

    def test_xp_orb_pickup_uses_player_collision_rect(self):
        player = DummyPlayer()
        player.collision_rect = pygame.Rect(42, 42, 10, 10)
        orb = XPOrb(50, 50)

        self.assertIs(orb.can_be_picked_up_by(player), True)

        player.collision_rect = pygame.Rect(200, 200, 10, 10)

        self.assertIs(orb.can_be_picked_up_by(player), False)


if __name__ == "__main__":
    unittest.main()
