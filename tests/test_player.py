import unittest

from models.player import Player
from config import (
    BASE_REQUIRED_XP,
    DAMAGE_PER_LEVEL,
    DEFENSE_HP_BONUS,
    DEFENSE_SHIELD_COOLDOWN,
    FAIRY_HEAL_AMOUNT,
    FAIRY_HEAL_FAST_COOLDOWN,
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

    def test_restore_progress_snapshot_rolls_back_level_stats(self):
        player = Player(10, 20)
        snapshot = player.get_progress_snapshot()
        required_level_1 = BASE_REQUIRED_XP + XP_PER_LEVEL

        player.add_xp(required_level_1 + 5)
        player.add_stars(3)
        player.restore_progress_snapshot(snapshot)

        self.assertEqual(player.level, 1)
        self.assertEqual(player.xp, 0)
        self.assertEqual(player.stars, 0)
        self.assertEqual(player.max_hp, PLAYER_MAX_HP)
        self.assertEqual(player.attack_damage, PLAYER_ATTACK_DAMAGE)

    def test_add_stars_ignores_non_positive_values(self):
        player = Player(10, 20)

        self.assertEqual(player.add_stars(2), 2)
        self.assertEqual(player.add_stars(0), 0)
        self.assertEqual(player.add_stars(-1), 0)
        self.assertEqual(player.stars, 2)

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

    def test_healing_branch_uses_reduced_cooldown_and_auto_rescue(self):
        player = Player(10, 20)
        player.unlocked_skills.update(
            {"fairy_heal", "fairy_cooldown", "fairy_rescue"}
        )
        player.hp = 20

        player.take_damage(1)

        self.assertEqual(player.hp, 19 + FAIRY_HEAL_AMOUNT)
        self.assertEqual(player.heal_cooldown, FAIRY_HEAL_FAST_COOLDOWN)
        self.assertIs(player.use_heal_skill(), False)

    def test_defense_branch_adds_hp_and_blocks_one_hit_per_cooldown(self):
        player = Player(10, 20)
        player.stars = 15

        self.assertIs(player.unlock_skill("defense_hp", 5), True)
        self.assertEqual(player.max_hp, PLAYER_MAX_HP + DEFENSE_HP_BONUS)
        self.assertEqual(player.hp, player.max_hp)
        self.assertIs(player.unlock_skill("defense_shield", 10), True)

        player.take_damage(25)
        self.assertEqual(player.hp, player.max_hp)
        self.assertEqual(player.shield_cooldown, DEFENSE_SHIELD_COOLDOWN)

        player.take_damage(25)
        self.assertEqual(player.hp, player.max_hp - 25)


if __name__ == "__main__":
    unittest.main()
