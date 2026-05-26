import unittest

from core.player import Player
from settings import (
    BASE_REQUIRED_XP,
    DAMAGE_PER_LEVEL,
    HP_PER_LEVEL,
    PLAYER_ATTACK_DAMAGE,
    PLAYER_MAX_HP,
    XP_PER_LEVEL,
)


class PlayerTest(unittest.TestCase):
    def test_add_xp_levels_up_and_carries_remaining_xp(self):
        player = Player(10, 20)
        required_level_1 = BASE_REQUIRED_XP + XP_PER_LEVEL

        levels_gained = player.add_xp(required_level_1 + 5)

        self.assertEqual(levels_gained, 1)
        self.assertEqual(player.level, 2)
        self.assertEqual(player.xp, 5)
        self.assertEqual(player.max_hp, PLAYER_MAX_HP + HP_PER_LEVEL)
        self.assertEqual(player.hp, player.max_hp)
        self.assertEqual(player.attack_damage, PLAYER_ATTACK_DAMAGE + DAMAGE_PER_LEVEL)

    def test_ignores_non_positive_xp(self):
        player = Player(10, 20)

        self.assertEqual(player.add_xp(0), 0)
        self.assertEqual(player.add_xp(-10), 0)
        self.assertEqual(player.level, 1)
        self.assertEqual(player.xp, 0)

    def test_damage_and_invincibility_cooldown(self):
        player = Player(10, 20)

        died = player.take_damage(25)
        player.start_damage_cooldown()

        self.assertIs(died, False)
        self.assertEqual(player.hp, PLAYER_MAX_HP - 25)
        self.assertIs(player.invincible, True)
        self.assertIs(player.take_damage(25), False)
        self.assertEqual(player.hp, PLAYER_MAX_HP - 25)

        player.update_cooldown(player.damage_cooldown_max)

        self.assertIs(player.invincible, False)


if __name__ == "__main__":
    unittest.main()
